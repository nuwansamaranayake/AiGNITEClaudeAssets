<#
.SYNOPSIS
  Reads a Supabase schema and writes API_CONTRACT.md.
.PARAMETER SchemaFile
  Path to the schema SQL.
.PARAMETER ProjectName
  Project name to embed in the contract.
.PARAMETER SupabaseUrl
  Project URL base.
.PARAMETER OutputFile
  Output path. Defaults to ./API_CONTRACT.md.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$SchemaFile,
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$SupabaseUrl,
  [string]$OutputFile = "API_CONTRACT.md"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $SchemaFile)) { throw "Schema file missing: $SchemaFile" }

$schema = Get-Content -Raw -LiteralPath $SchemaFile

$tableRegex = [regex]'(?im)^\s*create\s+table\s+(if\s+not\s+exists\s+)?(?<name>\w+)\s*\('
$tables = @()
foreach ($m in $tableRegex.Matches($schema)) {
  $tables += $m.Groups['name'].Value
}
$tables = $tables | Sort-Object -Unique

if ($tables.Count -eq 0) {
  Write-Warning "No tables found in schema. Generating empty contract."
}

$endpointRows = @()
$endpointRows += "| Method | URL | Purpose | Auth |"
$endpointRows += "|--------|-----|---------|------|"

foreach ($t in $tables) {
  $endpointRows += "| GET    | ``$SupabaseUrl/rest/v1/$t?select=*`` | List rows in $t | Required |"
  $endpointRows += "| POST   | ``$SupabaseUrl/rest/v1/$t`` | Insert a row into $t | Required |"
  $endpointRows += "| PATCH  | ``$SupabaseUrl/rest/v1/$t?id=eq.<id>`` | Update a row in $t | Required |"
  $endpointRows += "| DELETE | ``$SupabaseUrl/rest/v1/$t?id=eq.<id>`` | Delete a row in $t | Required |"
}

$endpointRows += "| POST   | ``$SupabaseUrl/auth/v1/token?grant_type=password`` | Sign in with email and password | None |"
$endpointRows += "| POST   | ``$SupabaseUrl/auth/v1/signup`` | Register a new user | None |"

$endpointBlock = $endpointRows -join "`n"

$skillRoot = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $skillRoot "assets\templates\API_CONTRACT.md.template"
$template = Get-Content -Raw -LiteralPath $templatePath

$today = (Get-Date).ToString("yyyy-MM-dd")
$rendered = $template `
  -replace "{{PROJECT_NAME}}", $ProjectName `
  -replace "{{DATE}}", $today `
  -replace "{{SUPABASE_URL}}", $SupabaseUrl `
  -replace "{{ENDPOINT_TABLE}}", $endpointBlock `
  -replace "{{CHANGELOG}}", "- $today: Initial contract generated from $SchemaFile."

Set-Content -LiteralPath $OutputFile -Value $rendered -Encoding utf8
Write-Host "WROTE $OutputFile ($($tables.Count) tables, $(($endpointRows.Count - 2)) endpoint rows)"
