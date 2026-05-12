<#
.SYNOPSIS
  Drives the asset extraction pipeline. One Gemini call per asset.
.PARAMETER ReferencePath
  Path to design/reference.png in the target project.
.PARAMETER ProjectDir
  Target Expo project root.
.PARAMETER AssetList
  Comma-separated list of asset subjects to extract (e.g. "water-drop,leaf,fire,settings-gear").
.PARAMETER StyleBlock
  The style descriptor every asset call reuses verbatim.
.PARAMETER DryRun
  Print the prompts that would run without calling Gemini.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ReferencePath,
  [Parameter(Mandatory=$true)][string]$ProjectDir,
  [Parameter(Mandatory=$true)][string]$AssetList,
  [string]$StyleBlock = "Rounded geometric icon, two-tone palette derived from reference, 2px stroke, soft inner shadow, no fills outside main shape",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $ReferencePath)) { throw "Reference image missing: $ReferencePath" }
if (!(Test-Path $ProjectDir)) { throw "Project directory missing: $ProjectDir" }

$outDir = Join-Path $ProjectDir "assets\extracted"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

$skillRoot = Split-Path -Parent $PSScriptRoot
$promptTemplatePath = Join-Path $skillRoot "assets\prompts\asset-extraction.txt"
$promptTemplate = Get-Content -Raw -LiteralPath $promptTemplatePath

$subjects = $AssetList -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ }

Write-Host "--- Extract assets ---"
Write-Host "Reference: $ReferencePath"
Write-Host "Project:   $ProjectDir"
Write-Host "Style:     $StyleBlock"
Write-Host "Subjects:  $($subjects -join ', ')"
Write-Host ""

foreach ($subject in $subjects) {
  $prompt = $promptTemplate `
    -replace "{{SUBJECT}}", $subject `
    -replace "{{STYLE_BLOCK}}", $StyleBlock

  $safeName = ($subject -replace '[^a-zA-Z0-9]+', '-').ToLower().Trim('-')
  $outPath = Join-Path $outDir "$safeName.png"

  if ($DryRun) {
    Write-Host "DRY  would call gemini-imagegen for '$subject' -> $outPath"
    Write-Host "PROMPT:"
    Write-Host $prompt
    Write-Host "---"
    continue
  }

  Write-Host "GEN  $subject -> $outPath"
  $promptFile = New-TemporaryFile
  Set-Content -LiteralPath $promptFile.FullName -Value $prompt -Encoding utf8
  Write-Host "PROMPT_FILE: $($promptFile.FullName)"
  Write-Host "Pass the prompt file to the gemini-imagegen skill in your Claude session for the actual generation."
  Write-Host "After the asset lands at $outPath, the skill validates the alpha channel and bounding box."
}

Write-Host ""
Write-Host "All assets queued. Validate each one with the next step in the skill."
