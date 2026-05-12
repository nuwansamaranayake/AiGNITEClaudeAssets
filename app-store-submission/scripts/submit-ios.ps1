<#
.SYNOPSIS
  Runs EAS submit for iOS after pre-flight checks.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER Profile
  EAS profile to submit. Defaults to production.
.PARAMETER DryRun
  Print the planned commands without running them.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [string]$Profile = "production",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Push-Location $ProjectDir

try {
  Write-Host "--- Pre-flight ---"

  $tests = "TEST_RESULTS.md"
  if (!(Test-Path $tests)) { throw "TEST_RESULTS.md missing. Run three-tier-test first." }
  $testsBody = Get-Content -Raw $tests
  $cutoff = (Get-Date).AddHours(-72)
  if ($testsBody -notmatch "Tier 3.*PASS") { throw "Tier 3 not marked PASS in TEST_RESULTS.md" }

  $audit = "SECURITY_AUDIT.md"
  if (!(Test-Path $audit)) { throw "SECURITY_AUDIT.md missing. Run security-audit first." }
  $auditBody = Get-Content -Raw $audit
  if ($auditBody -notmatch "GREEN") { throw "Security audit is not GREEN. Resolve findings first." }

  $appJson = "app.json"
  if (!(Test-Path $appJson)) { throw "app.json missing." }
  $cfg = Get-Content -Raw $appJson | ConvertFrom-Json
  if (-not $cfg.expo.ios.bundleIdentifier) { throw "iOS bundle identifier missing in app.json" }

  Write-Host "Pre-flight OK. Building and submitting."

  if ($DryRun) {
    Write-Host "DRY  would run: eas build --profile $Profile --platform ios"
    Write-Host "DRY  would run: eas submit --profile $Profile --platform ios --latest"
    exit 0
  }

  & eas build --profile $Profile --platform ios --non-interactive
  if ($LASTEXITCODE -ne 0) { throw "eas build failed" }

  & eas submit --profile $Profile --platform ios --latest --non-interactive
  if ($LASTEXITCODE -ne 0) { throw "eas submit failed" }

  Write-Host ""
  Write-Host "iOS submission uploaded."
  Write-Host "Next: log in to App Store Connect, complete the metadata if missing, and tap Submit for Review."
  Write-Host "Deep link: https://appstoreconnect.apple.com/apps"
}
finally {
  Pop-Location
}
