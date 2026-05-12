<#
.SYNOPSIS
  Renders the AiGNITE privacy policy and uploads it to contact.aigniteconsulting.ai.
.PARAMETER ProjectDir
  Path to the Expo project.
.PARAMETER Slug
  URL slug under /privacy/. Defaults to the project folder name.
.PARAMETER ControllerEntity
  AiGNITE Consulting LLC (US) or AiGNITE Software Pvt Ltd (Sri Lanka).
.PARAMETER ContactEmail
  Privacy contact email.
.PARAMETER DryRun
  Render the policy locally without uploading.
#>

[CmdletBinding()]
param(
  [string]$ProjectDir = ".",
  [string]$Slug,
  [string]$ControllerEntity = "AiGNITE Consulting LLC",
  [string]$ContactEmail = "privacy@aigniteconsulting.ai",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Push-Location $ProjectDir

try {
  if (-not $Slug) { $Slug = ((Get-Location).Path | Split-Path -Leaf).ToLower() -replace '[^a-z0-9]+', '-' }

  $skillRoot = Split-Path -Parent $PSScriptRoot
  $templatePath = Join-Path $skillRoot "assets\templates\privacy-policy.md.template"
  $template = Get-Content -Raw $templatePath

  $projectName = (Get-Location).Path | Split-Path -Leaf

  $dataYamlPath = "store\data-collection.yaml"
  $tableBody = if (Test-Path $dataYamlPath) {
    $rows = @("| Data type | Purpose | Retention | Shared with |", "|-----------|---------|-----------|-------------|")
    $yaml = Get-Content -Raw $dataYamlPath
    foreach ($line in ($yaml -split "`n")) {
      if ($line -match '^\s*- name:\s*"(.+)"') { $current = @{ name = $matches[1] } }
      if ($line -match '^\s*purpose:\s*"(.+)"' -and $current) { $current.purpose = $matches[1] }
      if ($line -match '^\s*retention:\s*"(.+)"' -and $current) { $current.retention = $matches[1] }
      if ($line -match '^\s*shared_with:\s*\[(.+)\]' -and $current) {
        $current.shared = $matches[1]
        $rows += "| $($current.name) | $($current.purpose) | $($current.retention) | $($current.shared) |"
      }
    }
    $rows -join "`n"
  } else {
    "| Email | Account auth | Until deletion | Supabase Auth |"
  }

  $today = (Get-Date).ToString("yyyy-MM-dd")
  $rendered = $template `
    -replace "{{PROJECT_NAME}}", $projectName `
    -replace "{{CONTROLLER_ENTITY}}", $ControllerEntity `
    -replace "{{CONTACT_EMAIL}}", $ContactEmail `
    -replace "{{DATA_COLLECTION_TABLE}}", $tableBody `
    -replace "{{LAST_UPDATED_DATE}}", $today

  $localOut = "store\privacy-policy.md"
  New-Item -ItemType Directory -Path (Split-Path $localOut) -Force | Out-Null
  Set-Content -LiteralPath $localOut -Value $rendered -Encoding utf8
  Write-Host "WROTE $localOut"

  $publicUrl = "https://contact.aigniteconsulting.ai/privacy/$Slug.html"

  if ($DryRun) {
    Write-Host "DRY  would upload $localOut to $publicUrl"
    exit 0
  }

  Write-Host "Upload step is environment-specific (Hostinger). Run the AiGNITE site deploy in a separate session to publish $localOut."
  Write-Host "Once live, verify: $publicUrl resolves to 200 before submitting to the store."
}
finally {
  Pop-Location
}
