<#
.SYNOPSIS
  Greps a project tree for hard-coded secrets.
.PARAMETER ProjectDir
  Path to the project root.
.PARAMETER DryRun
  No-op flag for parity with other scripts.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$patterns = @(
  @{ Name = "Stripe live secret";   Regex = "sk_live_[0-9a-zA-Z]{20,}" },
  @{ Name = "Stripe test secret";   Regex = "sk_test_[0-9a-zA-Z]{20,}" },
  @{ Name = "AWS access key";       Regex = "AKIA[0-9A-Z]{16}" },
  @{ Name = "GitHub PAT";           Regex = "ghp_[0-9a-zA-Z]{36}" },
  @{ Name = "Slack bot token";      Regex = "xoxb-[0-9a-zA-Z\-]{20,}" },
  @{ Name = "Private key block";    Regex = "-----BEGIN [A-Z ]*PRIVATE KEY-----" },
  @{ Name = "Supabase service JWT"; Regex = "eyJ[A-Za-z0-9_=\-]{20,}\.eyJ[A-Za-z0-9_=\-]{20,}\.[A-Za-z0-9_=\-]+" }
)

$exclude = @(
  "node_modules", ".expo", "dist", ".git", "ios\Pods", "android\build",
  ".next", ".turbo", "coverage"
)

$findings = @()

Get-ChildItem -Path $ProjectDir -Recurse -File -Force -ErrorAction SilentlyContinue |
  Where-Object {
    $path = $_.FullName
    -not ($exclude | Where-Object { $path -match [regex]::Escape("\$_") })
  } |
  Where-Object { $_.Length -lt 1MB } |
  Where-Object { $_.Extension -in @(".ts", ".tsx", ".js", ".jsx", ".json", ".env", ".md", ".sh", ".ps1", ".sql", ".toml", ".yaml", ".yml") -or $_.Name -match "^\.env" } |
  ForEach-Object {
    $file = $_.FullName
    try {
      $content = Get-Content -Raw -LiteralPath $file -ErrorAction Stop
    } catch { return }
    foreach ($p in $patterns) {
      if ($content -match $p.Regex) {
        $line = ((Select-String -Path $file -Pattern $p.Regex -ErrorAction SilentlyContinue) | Select-Object -First 1).LineNumber
        $findings += [PSCustomObject]@{
          File = $file
          Line = $line
          Pattern = $p.Name
          Severity = "Critical"
          CWE = "CWE-798"
        }
      }
    }
  }

if ($findings.Count -eq 0) {
  Write-Host "OK   No hard-coded secrets detected."
  exit 0
}

Write-Host "--- Secret scan findings ---"
$findings | Format-Table -AutoSize
exit 1
