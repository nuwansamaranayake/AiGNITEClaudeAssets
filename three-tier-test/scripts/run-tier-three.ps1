<#
.SYNOPSIS
  Runs tier three (physical device) of the three-tier test. Prints a manual checklist
  and waits for the user to type tier3:PASS or tier3:FAIL.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER Tester
  Name of the human running the checklist.
.PARAMETER DryRun
  Print the checklist without waiting for input.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [string]$Tester = $env:USERNAME,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Push-Location $ProjectDir

try {
  $skillRoot = Split-Path -Parent $PSScriptRoot
  $checklistTemplate = Join-Path $skillRoot "assets\templates\manual-checklist.md.template"

  $projectName = (Get-Location | Split-Path -Leaf)
  $checklistOut = Join-Path $ProjectDir "MANUAL_CHECKLIST.md"

  $rendered = (Get-Content -Raw $checklistTemplate) -replace "{{PROJECT_NAME}}", $projectName
  Set-Content -LiteralPath $checklistOut -Value $rendered -Encoding utf8
  Write-Host "WROTE $checklistOut"

  Write-Host ""
  Write-Host "--- Tier 3: Physical device ---"
  Write-Host "Open the development build on your phone now."
  Write-Host "Use the QR code printed by your most recent 'eas build --profile development' run."
  Write-Host "Work through MANUAL_CHECKLIST.md item by item."
  Write-Host ""

  if ($DryRun) {
    Write-Host "DRY  would now wait for tier3:PASS or tier3:FAIL."
    exit 0
  }

  $response = Read-Host "Type tier3:PASS or tier3:FAIL"
  $today = (Get-Date).ToString("yyyy-MM-dd HH:mm")

  $status = if ($response -match "^tier3:PASS$") { "PASS" } else { "FAIL" }

  $resultsPath = Join-Path $ProjectDir "TEST_RESULTS.md"
  if (!(Test-Path $resultsPath)) {
    Set-Content -LiteralPath $resultsPath -Value "# Test Results`n`n" -Encoding utf8
  }
  Add-Content -LiteralPath $resultsPath -Value "- Tier 3 (physical, $Tester): $status at $today"

  Write-Host ""
  Write-Host "Tier 3: $status. Logged to $resultsPath."
  if ($status -eq "PASS") { exit 0 } else { exit 1 }
}
finally {
  Pop-Location
}
