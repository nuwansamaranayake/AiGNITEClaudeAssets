<#
.SYNOPSIS
  Runs EAS submit for Android after pre-flight checks.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER Profile
  EAS profile to submit. Defaults to production.
.PARAMETER Track
  Google Play track. Defaults to internal.
.PARAMETER DryRun
  Print planned commands without running them.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [string]$Profile = "production",
  [ValidateSet("internal", "alpha", "beta", "production")][string]$Track = "internal",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Push-Location $ProjectDir

try {
  Write-Host "--- Pre-flight ---"
  if (!(Test-Path "TEST_RESULTS.md")) { throw "TEST_RESULTS.md missing. Run three-tier-test first." }
  if (!(Test-Path "SECURITY_AUDIT.md")) { throw "SECURITY_AUDIT.md missing. Run security-audit first." }
  $tr = Get-Content -Raw "TEST_RESULTS.md"
  $sa = Get-Content -Raw "SECURITY_AUDIT.md"
  if ($tr -notmatch "Tier 3.*PASS") { throw "Tier 3 not PASS" }
  if ($sa -notmatch "GREEN") { throw "Security audit not GREEN" }

  $appJson = Get-Content -Raw "app.json" | ConvertFrom-Json
  if (-not $appJson.expo.android.package) { throw "Android package missing in app.json" }

  if ($DryRun) {
    Write-Host "DRY  would run: eas build --profile $Profile --platform android"
    Write-Host "DRY  would run: eas submit --profile $Profile --platform android --track $Track"
    exit 0
  }

  & eas build --profile $Profile --platform android --non-interactive
  if ($LASTEXITCODE -ne 0) { throw "eas build failed" }

  & eas submit --profile $Profile --platform android --track $Track --latest --non-interactive
  if ($LASTEXITCODE -ne 0) { throw "eas submit failed" }

  Write-Host ""
  Write-Host "Android submission uploaded to $Track track."
  Write-Host "Next: log in to Google Play Console, complete the Data Safety form, and promote when ready."
  Write-Host "Deep link: https://play.google.com/console/u/0/developers"
}
finally {
  Pop-Location
}
