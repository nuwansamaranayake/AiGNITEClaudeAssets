<#
.SYNOPSIS
  Reports the remaining Higgsfield credit balance. Exits non-zero if balance is below MinBalance.
.PARAMETER MinBalance
  Minimum acceptable balance. Defaults to 20.
.PARAMETER PrintOnly
  Print balance and return zero regardless.
.PARAMETER DryRun
  Print plan only.
#>

[CmdletBinding()]
param(
  [int]$MinBalance = 20,
  [switch]$PrintOnly,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if ($DryRun) {
  Write-Host "DRY  would call Higgsfield MCP balance tool (e.g. get_credit_balance)"
  Write-Host "DRY  would compare to MinBalance=$MinBalance"
  exit 0
}

# The hosted Higgsfield MCP exposes a balance tool. Exact name varies by server version.
# This script is intended to be invoked by the orchestrating Claude session, which
# calls the MCP tool through Claude Code's MCP transport and writes the balance to
# the path passed via the environment variable HIGGSFIELD_BALANCE_FILE.

$balanceFile = $env:HIGGSFIELD_BALANCE_FILE
if (-not $balanceFile) {
  $balanceFile = Join-Path $PWD ".higgsfield-balance"
}

if (!(Test-Path $balanceFile)) {
  Write-Host "FAIL balance file not found at $balanceFile."
  Write-Host "     Run the higgsfield-media skill in your Claude session, which"
  Write-Host "     calls the MCP balance tool and writes the result to this path."
  exit 1
}

$raw = (Get-Content -Raw $balanceFile).Trim()
$balance = 0
if (-not [int]::TryParse($raw, [ref]$balance)) {
  Write-Host "FAIL balance file does not contain an integer: '$raw'"
  exit 1
}

Write-Host "Higgsfield credit balance: $balance"

if ($PrintOnly) { exit 0 }

if ($balance -lt $MinBalance) {
  Write-Host "FAIL balance $balance is below MinBalance $MinBalance."
  Write-Host "     Top up the Plus plan or wait for the monthly refresh."
  exit 1
}

Write-Host "OK   balance is above MinBalance ($MinBalance)."
exit 0
