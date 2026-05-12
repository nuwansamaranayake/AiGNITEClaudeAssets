<#
.SYNOPSIS
  Bootstraps a Supabase project for an AiGNITE mobile app.
.PARAMETER ProjectName
  Supabase project name (often matches the app slug).
.PARAMETER Region
  Hostinger VPS region nearest users. Map: us-east, us-west, mumbai, frankfurt.
.PARAMETER SchemaFile
  Path to the schema SQL to apply. Defaults to ./supabase/migrations/0001_init.sql.
.PARAMETER ExpectedTables
  Expected count of tables in the public schema after migration.
.PARAMETER OnePasswordVault
  Optional 1Password vault name to back up keys.
.PARAMETER DryRun
  Print actions without executing them.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][ValidateSet("us-east","us-west","mumbai","frankfurt")][string]$Region,
  [string]$SchemaFile = "supabase/migrations/0001_init.sql",
  [Parameter(Mandatory=$true)][int]$ExpectedTables,
  [string]$OnePasswordVault = "",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Run([string]$cmd) {
  if ($DryRun) { Write-Host "DRY  $cmd"; return }
  Write-Host "RUN  $cmd"
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) { throw "Command failed: $cmd" }
}

# Pre-flight
Write-Host "--- Pre-flight ---"
$null = & supabase --version 2>$null
if ($LASTEXITCODE -ne 0) {
  throw "Supabase CLI not found. Install: npm install -g supabase"
}
if (!(Test-Path "CLAUDE.md")) {
  Write-Warning "CLAUDE.md missing at project root. Did you run mobile-app-scaffold first?"
}
if (!(Test-Path ".env.local.example")) {
  Write-Warning ".env.local.example missing at project root."
}

# Step 1: init local supabase config if missing
if (!(Test-Path "supabase\config.toml")) {
  Run "supabase init"
}

# Step 2: create the remote project if needed
Write-Host "--- Step 2: ensure remote project ---"
$listOutput = & supabase projects list --output json 2>$null
$projects = if ($listOutput) { $listOutput | ConvertFrom-Json } else { @() }
$existing = $projects | Where-Object { $_.name -eq $ProjectName }
if (-not $existing) {
  Run "supabase projects create '$ProjectName' --region $Region --interactive=false"
  $listOutput = & supabase projects list --output json
  $projects = $listOutput | ConvertFrom-Json
  $existing = $projects | Where-Object { $_.name -eq $ProjectName }
}
if (-not $existing) { throw "Could not create or find project $ProjectName" }
$ref = $existing.id
Write-Host "Project ref: $ref"

Run "supabase link --project-ref $ref"

# Step 3: count tables before
$verifyScript = Join-Path $PSScriptRoot "verify-tables.ps1"
$beforeCount = & pwsh -File $verifyScript -OnlyCount -ProjectRef $ref
Write-Host "Tables before migration: $beforeCount"

# Step 4: apply migration
if (!(Test-Path $SchemaFile)) { throw "Schema file missing: $SchemaFile" }
Run "supabase db push --include-all"

# Step 5: verify table count
& pwsh -File $verifyScript -ProjectRef $ref -ExpectedTables $ExpectedTables
if ($LASTEXITCODE -ne 0) { throw "Table count verification failed. Aborting." }

# Step 6: generate API contract
$contractScript = Join-Path $PSScriptRoot "generate-contract.ps1"
& pwsh -File $contractScript -SchemaFile $SchemaFile -ProjectName $ProjectName -SupabaseUrl "https://$ref.supabase.co"

# Step 7: fetch keys
Write-Host "--- Step 7: fetch keys ---"
$apiKeysJson = & supabase projects api-keys --project-ref $ref --output json
$apiKeys = $apiKeysJson | ConvertFrom-Json
$anon = ($apiKeys | Where-Object { $_.name -eq "anon" }).api_key
$service = ($apiKeys | Where-Object { $_.name -eq "service_role" }).api_key

# Step 8: write env.local
$envPath = ".env.local"
$existingEnv = if (Test-Path $envPath) { Get-Content $envPath -Raw } else { "" }
$newEntries = @"
EXPO_PUBLIC_SUPABASE_URL=https://$ref.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=$anon
SUPABASE_SERVICE_ROLE_KEY=$service
"@
if ($existingEnv -notmatch "EXPO_PUBLIC_SUPABASE_URL=") {
  Add-Content -LiteralPath $envPath -Value $newEntries
  Write-Host "Wrote keys to $envPath"
} else {
  Write-Warning "$envPath already has Supabase keys. Skipping write. Update manually if needed."
}

# Step 9: optional 1Password backup
if ($OnePasswordVault) {
  $opAvailable = $null -ne (Get-Command op -ErrorAction SilentlyContinue)
  if ($opAvailable) {
    $entryName = "$ProjectName-supabase"
    Run "op item create --vault '$OnePasswordVault' --category 'API Credential' --title '$entryName' SUPABASE_URL='https://$ref.supabase.co' SUPABASE_ANON_KEY='$anon' SUPABASE_SERVICE_ROLE_KEY='$service'"
  } else {
    Write-Warning "1Password CLI (op) not installed. Skipping vault backup."
  }
}

# Summary
Write-Host ""
Write-Host "--- supabase-bootstrap complete ---"
Write-Host "Project:      $ProjectName"
Write-Host "Region:       $Region"
Write-Host "URL:          https://$ref.supabase.co"
Write-Host "API contract: ./API_CONTRACT.md"
Write-Host "Env file:     ./$envPath"
Write-Host ""
Write-Host "Next: fill SMOKE_TEST_TOKEN in .env.local with a test user JWT, then run 'make smoke'."
