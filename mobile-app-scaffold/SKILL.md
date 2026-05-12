---
name: mobile-app-scaffold
description: Generates a production-ready Expo React Native project pre-wired for AiGNITE conventions in under sixty seconds. Use this skill whenever the user mentions building a mobile app, scaffolding an Expo project, starting a new React Native app, mobile boilerplate, Expo scaffold, or kicking off a mobile project, even if they do not name the skill explicitly.
---

# mobile-app-scaffold

## Purpose

Output a complete Expo project tree with AiGNITE conventions baked in. Supabase client wired. MCP client wired. Smoke test wired to real business endpoints. CLAUDE.md with engineering standards seeded at the project root.

## When to trigger

Trigger on these user phrases. Match loosely.

- "build a mobile app"
- "scaffold an Expo project"
- "new React Native app"
- "start a mobile project"
- "Expo scaffold"
- "mobile app boilerplate"
- "kick off a mobile app"
- "set up a React Native repo"

## Inputs to collect

Before scaffolding, collect:

1. App name (human readable, e.g. "FloodPulse Mobile")
2. Bundle ID (reverse DNS, e.g. "com.aignite.floodpulse")
3. Target output directory (default: current working directory)
4. Optional MCP server URL the app will talk to

If the user has supplied any of these in the trigger message, parse them out and skip the matching prompt.

## What the skill produces

A complete Expo project at the target directory containing:

- `app.json` and `eas.json` with bundle ID and owner placeholders filled
- Folder layout: `app/` (Expo Router), `components/`, `lib/`, `hooks/`, `services/`, `assets/`
- `lib/supabase.ts` with client init and RLS-aware query helpers
- `services/mcp-client.ts` pointed at the supplied MCP server URL
- `.env.local.example` listing every variable the project needs
- `CLAUDE.md` at project root with the AiGNITE engineering standards
- `Makefile` with three targets: `make check`, `make up`, `make smoke`
- `scripts/smoke-test.sh` curling real business endpoints with a real token, counting DB tables
- `.gitignore`, `tsconfig.json` (strict), `eslint.config.js`, `prettier.config.js`
- ESLint rule blocking em dashes in source

## Smoke test contract

The generated `make smoke` calls real business endpoints. Health-only smoke tests are not acceptable. When a developer adds a new endpoint, the smoke test breaks until they add a probe for it. Document this rule in the generated `CLAUDE.md`.

## Execution flow

1. Parse inputs from the trigger message. Ask for missing values one at a time.
2. Run `scripts/scaffold.ps1` with the collected parameters.
3. The script writes every file using the templates in `assets/templates/`.
4. Run `scripts/verify-scaffold.ps1` to confirm every required file exists.
5. Print a summary table of files written.
6. Suggest the next step: run `npm install`, then `npx expo start`.

## Engineering standards baked into the output

The generated `CLAUDE.md` enforces these rules in every downstream session:

1. Root-cause fixes only. Curl failing endpoints, query the database, read logs before any fix.
2. Smoke tests verify real business endpoints, not health checks.
3. No silent mock data fallbacks outside development.
4. Verify table count after every database migration.
5. Maintain an API contract document mapping every frontend URL to its backend route.

See [references/aignite-coding-standards.md](references/aignite-coding-standards.md) for the full text.

## File and folder conventions

See [references/expo-conventions.md](references/expo-conventions.md) and [references/folder-layout.md](references/folder-layout.md).

## Failure modes

- Missing app name or bundle ID. Prompt the user. Do not invent placeholders.
- Target directory exists and is non-empty. Stop. Ask the user to confirm overwrite.
- Bundle ID does not match reverse-DNS format. Reject and ask again.
- MCP server URL supplied but unreachable. Warn but proceed. Note in the post-scaffold summary.

## Post-scaffold checklist for the user

Print this to the user after a successful scaffold:

1. `cd <project>`
2. `cp .env.local.example .env.local`
3. Fill `.env.local` with real keys
4. `npm install`
5. `npx expo start`
6. Open `make smoke` and add probes for the endpoints your app will hit

## Composes with

- `mvp-design-framework` runs before this skill to define what the app does
- `supabase-bootstrap` runs after to stand up the database
- `security-audit` runs before any TestFlight or Play submission
- `three-tier-test` runs before declaring a build ready
- `app-store-submission` ships the build to stores
- `mcp-to-mobile` orchestrates the whole pipeline starting from an MCP URL
