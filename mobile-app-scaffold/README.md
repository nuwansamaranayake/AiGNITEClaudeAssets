# mobile-app-scaffold

Part of the AiGNITE Claude Skills.

## What it does

Generates a production-ready Expo React Native project pre-wired for AiGNITE conventions in under sixty seconds. Output includes Supabase client, MCP client, smoke test, engineering standards, EAS config, ESLint with an em-dash ban, and a Makefile with three targets.

## When it triggers

Phrases like "build a mobile app", "scaffold an Expo project", "new React Native app", "mobile app boilerplate", or "kick off a mobile project".

## Install manually

Copy the folder into your user-level Claude skills directory:

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\mobile-app-scaffold" `
  -Destination "$env:USERPROFILE\.claude\skills\mobile-app-scaffold" -Force
```

Or run the suite installer at the repo root:

```powershell
.\INSTALL.ps1
```

## Files

- `SKILL.md` - the skill definition Claude reads.
- `references/` - Expo conventions, engineering standards, folder layout.
- `assets/templates/` - the file templates the skill stamps out.
- `scripts/scaffold.ps1` - the entry point.
- `scripts/verify-scaffold.ps1` - post-scaffold verification.
- `evals/evals.json` - trigger-prompt test cases.

## Composes with

- `mvp-design-framework` runs before this skill to define the MVP scope.
- `supabase-bootstrap` runs after to stand up the database.
- `security-audit`, `three-tier-test`, `app-store-submission` run downstream.
- `mcp-to-mobile` orchestrates the full pipeline from an MCP URL.

## License

See LICENSE at the repo root.
