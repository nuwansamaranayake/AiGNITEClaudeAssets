<#
.SYNOPSIS
  Verifies every required file exists in a scaffolded AiGNITE Expo project.
.PARAMETER ProjectDir
  Path to the scaffolded project.
.PARAMETER DryRun
  No-op flag for parity with scaffold.ps1.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ProjectDir,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$required = @(
  "app.json",
  "eas.json",
  "CLAUDE.md",
  "Makefile",
  "package.json",
  "tsconfig.json",
  "eslint.config.js",
  "prettier.config.js",
  ".env.local.example",
  ".gitignore",
  "lib/supabase.ts",
  "services/mcp-client.ts",
  "scripts/smoke-test.sh"
)

$requiredDirs = @(
  "app", "components", "lib", "hooks", "services", "assets", "scripts"
)

$missing = @()
$present = @()

foreach ($d in $requiredDirs) {
  $p = Join-Path $ProjectDir $d
  if (Test-Path -PathType Container $p) { $present += "DIR  $d" } else { $missing += "DIR  $d" }
}

foreach ($f in $required) {
  $p = Join-Path $ProjectDir $f
  if (Test-Path -PathType Leaf $p) { $present += "FILE $f" } else { $missing += "FILE $f" }
}

Write-Host "--- Verify scaffold: $ProjectDir ---"
foreach ($p in $present) { Write-Host "OK   $p" }
foreach ($m in $missing) { Write-Host "MISS $m" }

if ($missing.Count -gt 0) {
  Write-Host ""
  Write-Host "Verification failed. $($missing.Count) item(s) missing."
  exit 1
}

Write-Host ""
Write-Host "Verification passed. $($present.Count) items present."
exit 0
