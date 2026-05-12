<#
.SYNOPSIS
  Captures screenshots at every required size from a running app on iPhone Mirroring or Android emulator.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER Platform
  ios or android.
.PARAMETER ScreenList
  Comma-separated list of named screens to capture (e.g. "home,detail,settings").
.PARAMETER DryRun
  Print the capture plan without running it.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [ValidateSet("ios", "android")][string]$Platform = "ios",
  [string]$ScreenList = "home,detail,settings",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$iosSizes = @(
  @{ name = "6.7"; w = 1290; h = 2796 },
  @{ name = "6.5"; w = 1284; h = 2778 },
  @{ name = "5.5"; w = 1242; h = 2208 }
)

$androidSizes = @(
  @{ name = "phone";    w = 1080; h = 1920 },
  @{ name = "tablet-7"; w = 1200; h = 1920 }
)

$sizes = if ($Platform -eq "ios") { $iosSizes } else { $androidSizes }
$screens = $ScreenList -split "," | ForEach-Object { $_.Trim() }

$outRoot = Join-Path $ProjectDir "store\screenshots\$Platform"

foreach ($size in $sizes) {
  $sizeDir = Join-Path $outRoot $size.name
  New-Item -ItemType Directory -Path $sizeDir -Force | Out-Null

  $order = 0
  foreach ($screen in $screens) {
    $order++
    $fileName = "{0:D2}-{1}.png" -f $order, $screen
    $out = Join-Path $sizeDir $fileName

    if ($DryRun) {
      Write-Host "DRY  capture $($size.name) ($($size.w)x$($size.h)) screen='$screen' -> $out"
      continue
    }

    Write-Host "CAP  $($size.name) screen='$screen' -> $out"
    Write-Host "     Use the orchestrating Claude session with Chrome DevTools MCP or computer-use to capture."
    Write-Host "     Target dimensions: $($size.w)x$($size.h)"
  }
}

Write-Host ""
Write-Host "Screenshots queued for capture. Run the captures through the orchestrating Claude session."
