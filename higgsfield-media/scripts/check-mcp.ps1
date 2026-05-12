<#
.SYNOPSIS
  Verifies the Higgsfield MCP server is connected to Claude Code.
.PARAMETER DryRun
  Print the check plan without executing it.
#>

[CmdletBinding()]
param(
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if ($DryRun) {
  Write-Host "DRY  would run: claude mcp list | findstr higgsfield"
  exit 0
}

$claudeAvailable = $null -ne (Get-Command claude -ErrorAction SilentlyContinue)
if (-not $claudeAvailable) {
  Write-Host "FAIL claude CLI not found on PATH."
  Write-Host "     Install Claude Code first: https://claude.com/download"
  exit 1
}

$output = & claude mcp list 2>&1 | Out-String
if ($output -match "higgsfield.*Connected") {
  Write-Host "OK   higgsfield MCP connected."
  exit 0
}

if ($output -match "higgsfield") {
  Write-Host "FAIL higgsfield is registered but not Connected."
  Write-Host ""
  Write-Host "Re-authenticate via the Claude Code /mcp panel."
  Write-Host "Or remove and re-add:"
  Write-Host "  claude mcp remove higgsfield"
  Write-Host "  claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp"
  exit 1
}

Write-Host "FAIL higgsfield MCP is not installed."
Write-Host ""
Write-Host "Install it with this one-line command:"
Write-Host ""
Write-Host "  claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp"
Write-Host ""
Write-Host "Then complete the OAuth flow that opens in your browser."
Write-Host "Verify with: claude mcp list"
exit 1
