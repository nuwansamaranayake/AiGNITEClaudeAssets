<#
.SYNOPSIS
  Lists tools exposed by an AiGNITE MCP server and applies the public-safe whitelist.
.PARAMETER McpUrl
  The MCP server URL (or AiGNITE shortcut: beacon-gom, regscope, recallwatch, floodpulse, airshield, cosmic-nexus).
.PARAMETER OutputFile
  Optional path to write the filtered tool list.
.PARAMETER DryRun
  Print plan only.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$McpUrl,
  [string]$OutputFile = "mcp-tools.json",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$shortcuts = @{
  "beacon-gom"    = "https://beacon.aigniteconsulting.ai/mcp"
  "regscope"      = "https://regscope.aigniteconsulting.ai/mcp"
  "recallwatch"   = "https://recallwatch.aigniteconsulting.ai/mcp"
  "floodpulse"    = "https://floodpulse.aigniteconsulting.ai/mcp"
  "airshield"     = "https://airshield.aigniteconsulting.ai/mcp"
  "cosmic-nexus"  = "https://beta.cosmicnexus.ai/mcp"
}

if ($shortcuts.ContainsKey($McpUrl)) {
  $resolved = $shortcuts[$McpUrl]
  Write-Host "Shortcut '$McpUrl' -> $resolved"
  $McpUrl = $resolved
}

$whitelists = @{
  "beacon.aigniteconsulting.ai"   = @("public_get_operator_summary","public_list_recent_incidents","public_search_incidents")
  "regscope.aigniteconsulting.ai" = @("public_get_rule_details","public_list_recent_rules","public_search_federal_register")
  "recallwatch.aigniteconsulting.ai" = @("public_list_recalls","public_search_recalls","public_get_recall_details")
  "floodpulse.aigniteconsulting.ai" = @("public_check_flood_zone","public_get_flood_alerts","public_get_water_levels")
  "airshield.aigniteconsulting.ai" = @("public_get_air_quality","public_get_aqi_forecast","public_get_facility_compliance")
  "beta.cosmicnexus.ai" = @("general_reading","full_life_reading","compatibility_analysis","analyze_career","analyze_health","analyze_marriage","analyze_spirituality","analyze_wealth","longevity_analyze","ask_astrology_question","followup_question")
}

$host = ([Uri]$McpUrl).Host
$whitelist = if ($whitelists.ContainsKey($host)) { $whitelists[$host] } else { @() }

if ($whitelist.Count -eq 0) {
  Write-Warning "No public-safe whitelist defined for host $host. The skill will refuse to expose any tools until the catalog is updated."
}

Write-Host "Calling tools/list on $McpUrl..."

if ($DryRun) {
  Write-Host "DRY  would POST tools/list to $McpUrl"
  Write-Host "DRY  whitelist for $host has $($whitelist.Count) entries"
  exit 0
}

$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "tools/list"
  params = @{}
} | ConvertTo-Json -Depth 4

$response = Invoke-RestMethod -Uri $McpUrl -Method Post `
  -Headers @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" } `
  -Body $body

$allTools = $response.result.tools
if (-not $allTools) { throw "No tools returned from $McpUrl" }

Write-Host "Server exposes $($allTools.Count) tools."

$filtered = $allTools | Where-Object { $whitelist -contains $_.name }
Write-Host "After whitelist: $($filtered.Count) tools allowed in mobile app."

$filtered | ForEach-Object {
  Write-Host "  - $($_.name) :: $($_.description)"
}

$out = @{
  mcp_url = $McpUrl
  host = $host
  all_tools = $allTools | ForEach-Object { $_.name }
  whitelisted = $filtered | ForEach-Object { @{ name = $_.name; description = $_.description; inputSchema = $_.inputSchema } }
  excluded = ($allTools | Where-Object { $whitelist -notcontains $_.name } | ForEach-Object { $_.name })
} | ConvertTo-Json -Depth 8

Set-Content -LiteralPath $OutputFile -Value $out -Encoding utf8
Write-Host ""
Write-Host "WROTE $OutputFile"
