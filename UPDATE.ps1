<#
.SYNOPSIS
  Pulls the latest commits from origin and re-installs every skill.
.PARAMETER Branch
  Branch to pull. Defaults to main.
.PARAMETER DryRun
  Show planned actions without executing them.
#>

[CmdletBinding()]
param(
  [string]$Branch = "main",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot

try {
  if (!(Test-Path ".git")) {
    throw "This is not a git repo. Clone the suite first, then run UPDATE.ps1."
  }

  Write-Host "--- AiGNITE Mobile Skills updater ---"
  Write-Host "Branch: $Branch"

  if ($DryRun) {
    Write-Host "DRY  would run: git fetch origin"
    Write-Host "DRY  would run: git checkout $Branch"
    Write-Host "DRY  would run: git pull --ff-only origin $Branch"
    Write-Host "DRY  would run: .\INSTALL.ps1"
    exit 0
  }

  & git fetch origin
  if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }

  & git checkout $Branch
  if ($LASTEXITCODE -ne 0) { throw "git checkout failed" }

  & git pull --ff-only origin $Branch
  if ($LASTEXITCODE -ne 0) { throw "git pull failed. Resolve conflicts manually before retrying." }

  & ".\INSTALL.ps1"
  exit $LASTEXITCODE
}
finally {
  Pop-Location
}
