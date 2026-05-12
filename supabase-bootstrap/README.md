# supabase-bootstrap

Part of the AiGNITE Claude Skills.

## What it does

Stands up a Supabase project for an AiGNITE mobile app in one command. Generates a schema with RLS on by default. Applies the migration. Verifies the post-migration table count and aborts if the count is off. Writes the project URL and keys to `.env.local`. Generates `API_CONTRACT.md`.

## When it triggers

Phrases like "add a database", "Supabase setup", "auth setup", "set up Postgres", "add user accounts", "wire up Supabase".

## Critical rule

Never skips the table count verification. See `references/govihub-postmortem.md`.

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\supabase-bootstrap" `
  -Destination "$env:USERPROFILE\.claude\skills\supabase-bootstrap" -Force
```

## Composes with

Runs after `mobile-app-scaffold`. The `API_CONTRACT.md` it produces is consumed by `security-audit` and `three-tier-test`.

## License

See LICENSE at the repo root.
