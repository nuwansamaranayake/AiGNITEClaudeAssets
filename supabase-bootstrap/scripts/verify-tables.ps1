<#
.SYNOPSIS
  Counts tables in the public schema of a Supabase project and compares to expected count.
.PARAMETER ProjectRef
  Supabase project ref (the subdomain prefix).
.PARAMETER ExpectedTables
  Expected number of tables. Skip the comparison if -OnlyCount is set.
.PARAMETER OnlyCount
  Print the count and exit zero. Used by the bootstrap script for pre-migration baseline.
.PARAMETER DryRun
  No-op for parity with other scripts.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ProjectRef,
  [int]$ExpectedTables = 0,
  [switch]$OnlyCount,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (!(Test-Path ".env.local")) {
  throw ".env.local missing. Cannot reach Supabase without keys."
}

$envContents = Get-Content ".env.local"
$urlLine = ($envContents | Where-Object { $_ -match "^EXPO_PUBLIC_SUPABASE_URL=" })
$anonLine = ($envContents | Where-Object { $_ -match "^EXPO_PUBLIC_SUPABASE_ANON_KEY=" })
$serviceLine = ($envContents | Where-Object { $_ -match "^SUPABASE_SERVICE_ROLE_KEY=" })

if (-not $urlLine -or -not $anonLine) {
  throw "Supabase URL or anon key missing in .env.local"
}

$url = ($urlLine -split "=", 2)[1].Trim()
$anon = ($anonLine -split "=", 2)[1].Trim()
$service = if ($serviceLine) { ($serviceLine -split "=", 2)[1].Trim() } else { $anon }

$headers = @{
  apikey = $service
  Authorization = "Bearer $service"
}

$attempt = 0
$count = $null
while ($attempt -lt 3) {
  try {
    $response = Invoke-RestMethod -Uri "$url/rest/v1/rpc/count_public_tables" -Method Post -Headers $headers -Body "{}" -ContentType "application/json"
    $count = [int]$response
    break
  } catch {
    $attempt++
    Start-Sleep -Seconds 2
    if ($attempt -ge 3) { throw "Could not query count_public_tables RPC: $($_.Exception.Message)" }
  }
}

if ($OnlyCount) {
  Write-Output $count
  exit 0
}

Write-Host "--- Table count verification ---"
Write-Host "Expected: $ExpectedTables"
Write-Host "Actual:   $count"

if ($count -ne $ExpectedTables) {
  Write-Host ""
  Write-Host "MIGRATION FAILURE: table count mismatch."
  Write-Host "Dumping current table list for debugging..."

  $listResponse = Invoke-RestMethod -Uri "$url/rest/v1/?select=*" -Method Get -Headers $headers -ErrorAction SilentlyContinue
  if ($listResponse) { $listResponse | ConvertTo-Json -Depth 3 | Out-Host }

  Write-Host ""
  Write-Host "See references/govihub-postmortem.md for why this check exists."
  exit 1
}

Write-Host "OK   Table count matches expected."
exit 0
