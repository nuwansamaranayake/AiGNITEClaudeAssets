<#
.SYNOPSIS
  Three-pass security audit driver. Identify, fix, re-audit.
.PARAMETER ProjectDir
  Path to the project root.
.PARAMETER ProjectName
  Project name. Defaults to the directory name.
.PARAMETER FixMediumAndLow
  If set, attempts to fix Medium and Low findings, not only Critical/High.
.PARAMETER DryRun
  Only run pass 1. Do not apply fixes.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [string]$ProjectName,
  [switch]$FixMediumAndLow,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $ProjectName) {
  $ProjectName = (Resolve-Path $ProjectDir).Path | Split-Path -Leaf
}

$today = (Get-Date).ToString("yyyy-MM-dd")
$validUntil = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")

$skillRoot = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $skillRoot "assets\templates\SECURITY_AUDIT.md.template"
$auditPath = Join-Path $ProjectDir "SECURITY_AUDIT.md"

# --- Pass 1: identify ---
Write-Host "--- Security audit pass 1: identify ---"

$findings = @()

$secretScript = Join-Path $PSScriptRoot "scan-secrets.ps1"
& pwsh -File $secretScript -ProjectDir $ProjectDir | Out-Null
if ($LASTEXITCODE -ne 0) {
  $findings += [PSCustomObject]@{
    Tier = "Critical"; CWE = "CWE-798"; Issue = "Hard-coded secrets detected. See scan-secrets.ps1 output."
  }
}

# .env exposure check
$envFiles = Get-ChildItem -Path $ProjectDir -Filter ".env*" -File -ErrorAction SilentlyContinue
foreach ($f in $envFiles) {
  $content = Get-Content -Raw -LiteralPath $f.FullName -ErrorAction SilentlyContinue
  if (-not $content) { continue }
  foreach ($line in ($content -split "`n")) {
    if ($line -match '^EXPO_PUBLIC_.*(SECRET|PRIVATE|SERVICE_ROLE|WEBHOOK)' -and -not ($line.Trim().StartsWith("#"))) {
      $findings += [PSCustomObject]@{
        Tier = "Critical"; CWE = "CWE-200"; Issue = "Secret-like env var exposed under EXPO_PUBLIC_: $line"
      }
    }
  }
}

# .gitignore check
$gitignorePath = Join-Path $ProjectDir ".gitignore"
$gitignore = if (Test-Path $gitignorePath) { Get-Content -Raw $gitignorePath } else { "" }
if ($gitignore -notmatch "\.env\.local") {
  $findings += [PSCustomObject]@{
    Tier = "High"; CWE = "CWE-798"; Issue = ".env.local not in .gitignore"
  }
}

# RLS open policies
$migrationDir = Join-Path $ProjectDir "supabase\migrations"
if (Test-Path $migrationDir) {
  Get-ChildItem $migrationDir -Filter "*.sql" | ForEach-Object {
    $sql = Get-Content -Raw $_.FullName
    if ($sql -match 'using\s*\(\s*true\s*\)') {
      $findings += [PSCustomObject]@{
        Tier = "High"; CWE = "CWE-732"; Issue = "RLS policy with 'using (true)' in $($_.Name). Confirm intentional public access."
      }
    }
  }
}

# console.log leak check
Get-ChildItem -Path $ProjectDir -Recurse -File -Include "*.ts","*.tsx","*.js","*.jsx" -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch "node_modules|\.expo|dist" } |
  ForEach-Object {
    $content = Get-Content -Raw $_.FullName -ErrorAction SilentlyContinue
    if (-not $content) { return }
    if ($content -match 'console\.log\([^)]*\b(body|token|password|secret|email|ssn)\b') {
      $findings += [PSCustomObject]@{
        Tier = "Medium"; CWE = "CWE-532"; Issue = "console.log mentions sensitive field in $($_.Name)"
      }
    }
  }

# CORS check
Get-ChildItem -Path $ProjectDir -Recurse -File -Include "*.ts","*.js" -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch "node_modules|\.expo|dist" } |
  ForEach-Object {
    $content = Get-Content -Raw $_.FullName -ErrorAction SilentlyContinue
    if (-not $content) { return }
    if ($content -match 'Allow-Origin.*\*' -and $content -match 'Allow-Credentials.*true') {
      $findings += [PSCustomObject]@{
        Tier = "Critical"; CWE = "CWE-942"; Issue = "CORS allows '*' origin with credentials enabled in $($_.Name)"
      }
    }
  }

$p1Counts = @{
  Critical = ($findings | Where-Object { $_.Tier -eq "Critical" }).Count
  High     = ($findings | Where-Object { $_.Tier -eq "High" }).Count
  Medium   = ($findings | Where-Object { $_.Tier -eq "Medium" }).Count
  Low      = ($findings | Where-Object { $_.Tier -eq "Low" }).Count
}

Write-Host "Pass 1 findings: Critical=$($p1Counts.Critical) High=$($p1Counts.High) Medium=$($p1Counts.Medium) Low=$($p1Counts.Low)"

$findingsBlock = if ($findings.Count -eq 0) {
  "No findings."
} else {
  ($findings | ForEach-Object { "- [$($_.Tier)] $($_.CWE): $($_.Issue)" }) -join "`n"
}

# Render audit document
$template = Get-Content -Raw $templatePath
$verdict = if ($p1Counts.Critical -eq 0 -and $p1Counts.High -eq 0) { "GREEN — safe to ship" } else { "RED — fix Critical and High before submission" }

$rendered = $template `
  -replace "{{PROJECT_NAME}}", $ProjectName `
  -replace "{{DATE}}", $today `
  -replace "{{P1_CRIT}}", $p1Counts.Critical `
  -replace "{{P1_HIGH}}", $p1Counts.High `
  -replace "{{P1_MED}}", $p1Counts.Medium `
  -replace "{{P1_LOW}}", $p1Counts.Low `
  -replace "{{P2_CRIT}}", "0" `
  -replace "{{P2_HIGH}}", "0" `
  -replace "{{P2_MED}}", "0" `
  -replace "{{P2_LOW}}", "0" `
  -replace "{{P3_CRIT}}", "0" `
  -replace "{{P3_HIGH}}", "0" `
  -replace "{{P3_MED}}", "0" `
  -replace "{{P3_LOW}}", "0" `
  -replace "{{OPEN_CRIT}}", $p1Counts.Critical `
  -replace "{{OPEN_HIGH}}", $p1Counts.High `
  -replace "{{OPEN_MED}}", $p1Counts.Medium `
  -replace "{{OPEN_LOW}}", $p1Counts.Low `
  -replace "{{VERDICT}}", $verdict `
  -replace "{{P1_FINDINGS}}", $findingsBlock `
  -replace "{{P2_RESOLUTIONS}}", "Pass 2 not yet run. Apply fixes and re-run with the orchestrating skill driver." `
  -replace "{{P3_REGRESSIONS}}", "Pass 3 not yet run." `
  -replace "{{OWNER}}", "TBD" `
  -replace "{{SIGNOFF_DATE}}", "TBD" `
  -replace "{{VALID_UNTIL}}", $validUntil

Set-Content -LiteralPath $auditPath -Value $rendered -Encoding utf8
Write-Host "WROTE $auditPath"

if ($DryRun) {
  Write-Host "Dry run complete. Pass 2 and 3 skipped."
  exit 0
}

if ($p1Counts.Critical -eq 0 -and $p1Counts.High -eq 0) {
  Write-Host "OK   No Critical or High findings. Pass 2 not needed."
  exit 0
}

Write-Host ""
Write-Host "Pass 2 (apply fixes) and Pass 3 (regression check) are interactive."
Write-Host "Re-run the skill in your Claude session and follow the prompts. The skill rewrites SECURITY_AUDIT.md after each pass."
exit 1
