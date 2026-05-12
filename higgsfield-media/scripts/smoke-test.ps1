<#
.SYNOPSIS
  End-to-end smoke test for the higgsfield-media skill.
.DESCRIPTION
  This script is the contract the orchestrating Claude session implements. It does
  not call the MCP directly because MCP tool calls flow through Claude Code. The
  Claude session reads this contract, performs each step via the appropriate MCP
  tool, and reports back. The script itself runs the file-validation pieces.
.PARAMETER ResultPath
  Path to the downloaded test PNG produced by the Claude session.
.PARAMETER DryRun
  Print the contract without enforcing.
#>

[CmdletBinding()]
param(
  [string]$ResultPath,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$contract = @"
SMOKE TEST CONTRACT (executed by Claude session, validated by this script)

Steps the orchestrating Claude session performs:

1. Verify MCP connected.
   scripts/check-mcp.ps1 must exit 0.

2. Read current credit balance.
   Call the Higgsfield balance tool, write to .higgsfield-balance file.
   scripts/check-balance.ps1 -PrintOnly must succeed.

3. Generate a 1024x1024 test image with Flux 2 Pro (unlimited on Plus, 0 credits).
   Prompt: "abstract emerald gradient, soft glow, vector style, no text, no watermark"
   Model: flux-2-pro
   Aspect ratio: 1:1

4. Download the returned URL to a temp file.
   Pass the local path as -ResultPath to this script.

5. This script then validates:
   - File exists
   - File is a real PNG (magic bytes match)
   - File size is at least 10KB

If all five steps pass, the smoke test is green.
"@

Write-Host $contract
Write-Host ""

if ($DryRun) {
  Write-Host "(dry run, no validation)"
  exit 0
}

if (-not $ResultPath) {
  Write-Host "FAIL no -ResultPath provided. The Claude session must pass the local path of the downloaded test PNG."
  exit 1
}

if (!(Test-Path $ResultPath)) {
  Write-Host "FAIL $ResultPath does not exist."
  exit 1
}

$info = Get-Item $ResultPath
if ($info.Length -lt 10KB) {
  Write-Host "FAIL $ResultPath is only $($info.Length) bytes. Expected at least 10KB."
  exit 1
}

$bytes = [System.IO.File]::ReadAllBytes($ResultPath)[0..7]
$expected = @(137, 80, 78, 71, 13, 10, 26, 10)
for ($i = 0; $i -lt 8; $i++) {
  if ($bytes[$i] -ne $expected[$i]) {
    Write-Host "FAIL $ResultPath is not a valid PNG (magic-byte mismatch at offset $i)."
    exit 1
  }
}

Write-Host "OK   smoke test passed."
Write-Host "     file:      $ResultPath"
Write-Host "     size:      $($info.Length) bytes"
Write-Host "     format:    PNG (magic bytes match)"
exit 0
