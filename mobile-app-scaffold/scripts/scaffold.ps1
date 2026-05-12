<#
.SYNOPSIS
  Scaffolds a new AiGNITE-conventioned Expo project from templates.
.PARAMETER AppName
  Human-readable app name. Example: "FloodPulse Mobile".
.PARAMETER BundleId
  Reverse-DNS bundle identifier. Example: "com.aignite.floodpulse".
.PARAMETER TargetDir
  Destination directory. Defaults to a slugified subfolder of the current dir.
.PARAMETER McpServerUrl
  Optional MCP server URL the app will talk to.
.PARAMETER EasOwner
  EAS account owner. Defaults to "aignite".
.PARAMETER DryRun
  Print actions without writing files.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$AppName,
  [Parameter(Mandatory=$true)][string]$BundleId,
  [string]$TargetDir,
  [string]$McpServerUrl = "",
  [string]$EasOwner = "aignite",
  [int]$ExpectedTableCount = 0,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Slugify([string]$s) {
  return ($s -replace '[^a-zA-Z0-9]+', '-').ToLower().Trim('-')
}

function Assert-BundleId([string]$id) {
  if ($id -notmatch '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$') {
    throw "Bundle ID must be reverse-DNS lowercase. Got: $id"
  }
}

function Render([string]$templatePath, [hashtable]$vars) {
  $text = Get-Content -Raw -LiteralPath $templatePath
  foreach ($k in $vars.Keys) {
    $text = $text -replace ("{{" + [regex]::Escape($k) + "}}"), [string]$vars[$k]
  }
  return $text
}

Assert-BundleId $BundleId

$slug = Slugify $AppName
if (-not $TargetDir) {
  $TargetDir = Join-Path (Get-Location) $slug
}

if (Test-Path $TargetDir) {
  $existing = Get-ChildItem $TargetDir -Force -ErrorAction SilentlyContinue
  if ($existing) {
    throw "Target directory exists and is non-empty: $TargetDir. Stop and confirm overwrite manually."
  }
}

$skillRoot = Split-Path -Parent $PSScriptRoot
$templates = Join-Path $skillRoot "assets\templates"

$vars = @{
  APP_NAME             = $AppName
  APP_SLUG             = $slug
  BUNDLE_ID            = $BundleId
  MCP_SERVER_URL       = $McpServerUrl
  EAS_OWNER            = $EasOwner
  EAS_PROJECT_ID       = "PLACEHOLDER_RUN_EAS_INIT"
  APPLE_ID             = "PLACEHOLDER_APPLE_ID"
  ASC_APP_ID           = "PLACEHOLDER_ASC_APP_ID"
  APPLE_TEAM_ID        = "PLACEHOLDER_APPLE_TEAM_ID"
  EXPECTED_TABLE_COUNT = "$ExpectedTableCount"
}

$plan = @(
  @{ src = "app.json.template";              dst = "app.json" },
  @{ src = "eas.json.template";              dst = "eas.json" },
  @{ src = "CLAUDE.md.template";             dst = "CLAUDE.md" },
  @{ src = "Makefile.template";              dst = "Makefile" },
  @{ src = "smoke-test.sh.template";         dst = "scripts/smoke-test.sh" },
  @{ src = "supabase-client.ts.template";    dst = "lib/supabase.ts" },
  @{ src = "mcp-client.ts.template";         dst = "services/mcp-client.ts" }
)

$dirs = @(
  "app", "app/(tabs)", "app/(auth)",
  "components", "lib", "hooks", "services",
  "assets", "scripts"
)

Write-Host "--- Scaffold plan ---"
Write-Host "App:        $AppName"
Write-Host "Slug:       $slug"
Write-Host "Bundle ID:  $BundleId"
Write-Host "Target:     $TargetDir"
Write-Host "MCP URL:    $McpServerUrl"
Write-Host ""

if ($DryRun) {
  foreach ($d in $dirs) { Write-Host "MKDIR  $TargetDir\$d" }
  foreach ($f in $plan) { Write-Host "WRITE  $TargetDir\$($f.dst)" }
  Write-Host "(dry run, no files written)"
  exit 0
}

New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Path (Join-Path $TargetDir $d) -Force | Out-Null
}

foreach ($f in $plan) {
  $srcPath = Join-Path $templates $f.src
  $dstPath = Join-Path $TargetDir $f.dst
  $rendered = Render $srcPath $vars
  $dstDir = Split-Path -Parent $dstPath
  if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
  Set-Content -LiteralPath $dstPath -Value $rendered -Encoding utf8
  Write-Host "WROTE  $($f.dst)"
}

# .env.local.example
$envExample = @'
EXPO_PUBLIC_SUPABASE_URL=https://YOUR-PROJECT.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY
EXPO_PUBLIC_MCP_SERVER_URL=
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY_SERVER_ONLY
SMOKE_TEST_TOKEN=YOUR_TEST_USER_JWT
'@
Set-Content -LiteralPath (Join-Path $TargetDir ".env.local.example") -Value $envExample -Encoding utf8
Write-Host "WROTE  .env.local.example"

# .gitignore
$gitignore = @'
node_modules/
.expo/
dist/
.env.local
*.log
.DS_Store
secrets/
'@
Set-Content -LiteralPath (Join-Path $TargetDir ".gitignore") -Value $gitignore -Encoding utf8
Write-Host "WROTE  .gitignore"

# tsconfig.json
$tsconfig = @'
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true
  },
  "include": ["**/*.ts", "**/*.tsx", "expo-env.d.ts"]
}
'@
Set-Content -LiteralPath (Join-Path $TargetDir "tsconfig.json") -Value $tsconfig -Encoding utf8
Write-Host "WROTE  tsconfig.json"

# eslint.config.js with em dash rule
$eslint = @'
const tseslint = require("typescript-eslint");

module.exports = tseslint.config(
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: { parser: tseslint.parser },
    plugins: { "@typescript-eslint": tseslint.plugin },
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Literal[value=/\\u2014/]",
          message: "No em dashes in source. AiGNITE style rule."
        },
        {
          selector: "TemplateElement[value.raw=/\\u2014/]",
          message: "No em dashes in source. AiGNITE style rule."
        }
      ],
      "@typescript-eslint/no-explicit-any": "error"
    }
  }
);
'@
Set-Content -LiteralPath (Join-Path $TargetDir "eslint.config.js") -Value $eslint -Encoding utf8
Write-Host "WROTE  eslint.config.js"

# prettier.config.js
$prettier = @'
module.exports = {
  semi: true,
  singleQuote: true,
  trailingComma: "es5",
  printWidth: 100,
  tabWidth: 2
};
'@
Set-Content -LiteralPath (Join-Path $TargetDir "prettier.config.js") -Value $prettier -Encoding utf8
Write-Host "WROTE  prettier.config.js"

# package.json
$pkg = @"
{
  "name": "$slug",
  "version": "0.1.0",
  "main": "expo-router/entry",
  "scripts": {
    "start": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios",
    "web": "expo start --web",
    "typecheck": "tsc --noEmit",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "dependencies": {
    "@react-native-async-storage/async-storage": "^1.23.1",
    "@supabase/supabase-js": "^2.45.0",
    "expo": "~52.0.0",
    "expo-router": "~4.0.0",
    "expo-secure-store": "~14.0.0",
    "react": "18.3.1",
    "react-native": "0.76.0",
    "react-native-url-polyfill": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "~18.3.0",
    "eslint": "^9.0.0",
    "prettier": "^3.3.0",
    "typescript": "~5.5.0",
    "typescript-eslint": "^8.0.0"
  },
  "private": true
}
"@
Set-Content -LiteralPath (Join-Path $TargetDir "package.json") -Value $pkg -Encoding utf8
Write-Host "WROTE  package.json"

Write-Host ""
Write-Host "--- Scaffold complete ---"
Write-Host "Next steps:"
Write-Host "  1. cd $TargetDir"
Write-Host "  2. cp .env.local.example .env.local && fill keys"
Write-Host "  3. npm install"
Write-Host "  4. npx expo start"
Write-Host "  5. Add real-endpoint probes to scripts/smoke-test.sh"
