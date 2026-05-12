<#
.SYNOPSIS
  Generates one Expo Router screen per whitelisted MCP tool.
.PARAMETER ProjectDir
  Path to the scaffolded Expo project.
.PARAMETER ToolsFile
  Path to the mcp-tools.json file produced by discover-tools.ps1.
.PARAMETER DryRun
  Print plan only.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ProjectDir,
  [Parameter(Mandatory=$true)][string]$ToolsFile,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $ProjectDir)) { throw "Project dir missing: $ProjectDir" }
if (!(Test-Path $ToolsFile)) { throw "Tools file missing: $ToolsFile" }

$tools = (Get-Content -Raw $ToolsFile | ConvertFrom-Json).whitelisted
if (-not $tools -or $tools.Count -eq 0) { throw "No whitelisted tools to generate." }

$skillRoot = Split-Path -Parent $PSScriptRoot
$screenTemplate = Get-Content -Raw (Join-Path $skillRoot "assets\templates\screen-from-tool.tsx.template")

$screensDir = Join-Path $ProjectDir "app\(tabs)"
New-Item -ItemType Directory -Path $screensDir -Force | Out-Null

function ToPascal([string]$s) {
  ($s -split '[_\-\s]' | ForEach-Object {
    if ($_ -and $_.Length -gt 0) { $_.Substring(0,1).ToUpper() + $_.Substring(1).ToLower() }
  }) -join ''
}

function ToTitle([string]$s) {
  ($s -split '[_\-]' | ForEach-Object {
    if ($_ -and $_.Length -gt 0) { $_.Substring(0,1).ToUpper() + $_.Substring(1).ToLower() }
  }) -join ' '
}

foreach ($tool in $tools) {
  $fileName = ($tool.name -replace '_', '-').ToLower() + ".tsx"
  $componentName = ToPascal $tool.name
  $title = ToTitle ($tool.name -replace '^public_', '')
  $description = if ($tool.description) { $tool.description } else { "" }
  $inputJson = $tool.inputSchema | ConvertTo-Json -Depth 10 -Compress

  $rendered = $screenTemplate `
    -replace "{{TOOL_NAME}}", $tool.name `
    -replace "{{TOOL_TITLE}}", $title `
    -replace "{{TOOL_DESCRIPTION}}", $description `
    -replace "{{COMPONENT_NAME}}", $componentName `
    -replace "{{INPUT_SCHEMA_JSON}}", $inputJson `
    -replace "{{MCP_SERVER_URL}}", ""

  $outPath = Join-Path $screensDir $fileName

  if ($DryRun) {
    Write-Host "DRY  would write $outPath"
    continue
  }

  Set-Content -LiteralPath $outPath -Value $rendered -Encoding utf8
  Write-Host "WROTE $outPath"
}

Write-Host ""
Write-Host "Generated $($tools.Count) tool screens."
Write-Host "Next: implement components/McpToolForm and components/SubscriptionGate from templates."
