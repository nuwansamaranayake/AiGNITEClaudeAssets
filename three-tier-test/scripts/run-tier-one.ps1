<#
.SYNOPSIS
  Runs tier one (Chrome + Playwright) of the three-tier test.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER BaseUrl
  URL of the running Expo web build. Defaults to http://localhost:8081.
.PARAMETER DryRun
  Print the planned commands without running them.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [string]$BaseUrl = "http://localhost:8081",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Push-Location $ProjectDir

try {
  Write-Host "--- Tier 1: Chrome / Playwright ---"
  Write-Host "Project: $((Get-Location).Path)"
  Write-Host "Base URL: $BaseUrl"

  if (!(Test-Path "playwright.config.ts") -and !(Test-Path "playwright.config.js")) {
    throw "No playwright.config found. See references/playwright-setup.md."
  }

  if ($DryRun) {
    Write-Host "DRY  would run: npx playwright test --reporter=line"
    exit 0
  }

  $env:PLAYWRIGHT_BASE_URL = $BaseUrl
  & npx playwright test --reporter=line
  $code = $LASTEXITCODE

  $today = (Get-Date).ToString("yyyy-MM-dd HH:mm")
  $status = if ($code -eq 0) { "PASS" } else { "FAIL" }

  $resultsPath = "TEST_RESULTS.md"
  if (!(Test-Path $resultsPath)) {
    Set-Content -LiteralPath $resultsPath -Value "# Test Results`n`n" -Encoding utf8
  }
  Add-Content -LiteralPath $resultsPath -Value "- Tier 1: $status at $today"

  Write-Host ""
  Write-Host "Tier 1: $status. Logged to $resultsPath."
  exit $code
}
finally {
  Pop-Location
}
