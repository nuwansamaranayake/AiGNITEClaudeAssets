<#
.SYNOPSIS
  Drives the screenshot-and-diff loop against a running Expo web build.
.PARAMETER ReferencePath
  Path to design/reference.png.
.PARAMETER ProjectDir
  Target Expo project root. The script reads the dev server URL from .expo-dev-url if present, else uses http://localhost:8081.
.PARAMETER Tolerance
  Match band: tight (3%), moderate (8%), loose (15%).
.PARAMETER MaxIterations
  Hard cap on iterations. Defaults to 10.
.PARAMETER DryRun
  Run a single comparison and exit without applying changes.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ReferencePath,
  [Parameter(Mandatory=$true)][string]$ProjectDir,
  [ValidateSet("tight", "moderate", "loose")][string]$Tolerance = "moderate",
  [int]$MaxIterations = 10,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$thresholds = @{ tight = 0.03; moderate = 0.08; loose = 0.15 }
$threshold = $thresholds[$Tolerance]

if (!(Test-Path $ReferencePath)) { throw "Reference missing: $ReferencePath" }
if (!(Test-Path $ProjectDir)) { throw "Project missing: $ProjectDir" }

$urlFile = Join-Path $ProjectDir ".expo-dev-url"
$devUrl = if (Test-Path $urlFile) { (Get-Content $urlFile -Raw).Trim() } else { "http://localhost:8081" }

$iterLog = Join-Path $ProjectDir "design\iterations.log"
$iterDir = Join-Path $ProjectDir "design\iterations"
New-Item -ItemType Directory -Path (Split-Path $iterLog) -Force | Out-Null
New-Item -ItemType Directory -Path $iterDir -Force | Out-Null

Write-Host "--- Screenshot loop ---"
Write-Host "Reference: $ReferencePath"
Write-Host "Dev URL:   $devUrl"
Write-Host "Threshold: $($threshold * 100)%"
Write-Host "Max iter:  $MaxIterations"
Write-Host ""

# This script orchestrates. The actual screenshot capture and diff happen via
# Chrome DevTools MCP and an image diff library in the Claude Code session.
# This file documents the contract so the session knows what to call.

$contract = @"
Iteration contract for the orchestrating Claude session:

1. Navigate the Chrome DevTools MCP to: $devUrl
2. Capture a screenshot at the reference image dimensions.
3. Save the capture to: design/iterations/iter-{NN}.png
4. Compute a perceptual diff between the capture and the reference.
5. If diff < $threshold, write "PASS" to design/iterations.log and exit.
6. If diff >= $threshold, produce a single-change adjustment prompt naming:
   - The metric that differs (spacing, color, radius, font, asset, shadow).
   - The exact value to change.
   - The file to edit (lib/theme.ts or a component path).
7. Apply the change. Save the new component or theme state.
8. Wait for hot reload.
9. Loop to step 1.

Stop conditions:
- diff < $threshold (PASS)
- iteration count >= $MaxIterations (HARD STOP, write FAIL)
- user types 'good enough' (USER ACCEPT)
- iteration would require a new asset (PAUSE, regenerate asset, then resume)
"@

Set-Content -LiteralPath $iterLog -Value $contract -Encoding utf8
Write-Host "WROTE $iterLog"

if ($DryRun) {
  Write-Host "Dry run complete. Inspect the contract and start the loop manually."
  exit 0
}

Write-Host ""
Write-Host "Hand control back to the orchestrating Claude session to run the loop."
Write-Host "The session reads $iterLog to drive each iteration."
