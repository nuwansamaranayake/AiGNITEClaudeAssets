<#
.SYNOPSIS
  Installs all AiGNITE Claude Skills into the user-level Claude Code skills directory.
.DESCRIPTION
  Copies each skill folder to %USERPROFILE%\.claude\skills, replacing any existing installation.
.PARAMETER DryRun
  Print the planned copies without executing them.
#>

[CmdletBinding()]
param(
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$targetRoot = "$env:USERPROFILE\.claude\skills"

if (!(Test-Path $targetRoot)) {
  Write-Host "Creating $targetRoot"
  if (-not $DryRun) { New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null }
}

$skills = @(
  "mobile-app-scaffold",
  "mvp-design-framework",
  "supabase-bootstrap",
  "security-audit",
  "design-from-mockup",
  "three-tier-test",
  "app-store-submission",
  "mcp-to-mobile",
  "higgsfield-media",
  "hermes-vps-deploy"
)

Write-Host "--- AiGNITE Claude Skills installer ---"
Write-Host "Source: $repoRoot"
Write-Host "Target: $targetRoot"
Write-Host ""

$installed = @()
$missing = @()

foreach ($skill in $skills) {
  $src = Join-Path $repoRoot $skill
  $dst = Join-Path $targetRoot $skill

  if (!(Test-Path $src)) {
    Write-Warning "Source missing: $src"
    $missing += $skill
    continue
  }

  if ($DryRun) {
    Write-Host "DRY  would install $skill -> $dst"
    continue
  }

  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  Copy-Item -Recurse -Path $src -Destination $dst
  $count = (Get-ChildItem $dst -Recurse -File | Measure-Object).Count
  Write-Host "OK   $skill ($count files)"
  $installed += $skill
}

Write-Host ""
Write-Host "Installed: $($installed.Count) skill(s)"
if ($missing.Count -gt 0) {
  Write-Host "Missing:   $($missing -join ', ')"
  exit 1
}

Write-Host ""
Write-Host "Open a new Claude Code session to pick up the installed skills."
Write-Host "Verify a mobile skill: 'Build a mobile app called Test with bundle id com.test.x'"
Write-Host "Verify the ops skill:  'Deploy Hermes Agent to my VPS at hermes.example.com via ssh alias myhost'"
exit 0
