<#
.SYNOPSIS
  Runs tier two (iPhone Mirroring or Android emulator) of the three-tier test.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER Platform
  ios or android.
.PARAMETER FlowFile
  Path to the Maestro flow YAML. Defaults to e2e/flow.yaml.
.PARAMETER DryRun
  Print the planned commands without running them.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [ValidateSet("ios", "android")][string]$Platform = "ios",
  [string]$FlowFile = "e2e/flow.yaml",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Push-Location $ProjectDir

try {
  Write-Host "--- Tier 2: Mirror / Emulator ---"
  Write-Host "Project:  $((Get-Location).Path)"
  Write-Host "Platform: $Platform"
  Write-Host "Flow:     $FlowFile"

  if (!(Test-Path $FlowFile)) {
    Write-Warning "Maestro flow not found at $FlowFile. Tier two needs a recorded walkthrough."
    Write-Host "Generate one with: maestro studio"
    if (-not $DryRun) { exit 1 }
  }

  $maestroAvailable = $null -ne (Get-Command maestro -ErrorAction SilentlyContinue)
  if (-not $maestroAvailable) {
    Write-Warning "maestro CLI not found. Install: brew install maestro (mac) or see docs."
    if (-not $DryRun) { exit 1 }
  }

  if ($DryRun) {
    Write-Host "DRY  would run: maestro test $FlowFile"
    exit 0
  }

  Write-Host "Make sure the dev build is installed and running on $Platform (Mirroring or emulator)."
  & maestro test $FlowFile
  $code = $LASTEXITCODE

  $today = (Get-Date).ToString("yyyy-MM-dd HH:mm")
  $status = if ($code -eq 0) { "PASS" } else { "FAIL" }

  $resultsPath = "TEST_RESULTS.md"
  if (!(Test-Path $resultsPath)) {
    Set-Content -LiteralPath $resultsPath -Value "# Test Results`n`n" -Encoding utf8
  }
  Add-Content -LiteralPath $resultsPath -Value "- Tier 2 ($Platform): $status at $today"

  Write-Host ""
  Write-Host "Tier 2 ($Platform): $status. Logged to $resultsPath."
  exit $code
}
finally {
  Pop-Location
}
