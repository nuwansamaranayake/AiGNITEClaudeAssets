---
name: supabase-bootstrap
description: Stands up a Supabase project for an AiGNITE mobile app, generates a schema with RLS on by default, verifies table count, produces an API contract document, and writes keys to .env.local in one command. Use this skill whenever the user mentions adding a database, Supabase setup, auth setup, setting up Postgres, adding user accounts, wiring up Supabase, or backing a mobile app with a database, even if they do not name the skill by name.
---

# supabase-bootstrap

## Purpose

Take an AiGNITE mobile project from "no backend" to "schema applied, RLS active, contract documented, table count verified" in one run.

## When to trigger

Trigger on these user phrases. Match loosely.

- "add a database"
- "Supabase setup"
- "auth setup"
- "database for my app"
- "set up Postgres"
- "add user accounts"
- "wire up Supabase"
- "stand up the backend"

## Inputs to collect

1. Project name (defaults to the current folder name)
2. Hostinger VPS region nearest users (us-east, us-west, mumbai, frankfurt)
3. Table list with columns (the skill asks for these, or reads them from MVP_SPEC.md if present)
4. Authentication mode (email-password, magic-link, oauth)
5. Optional: 1Password vault name to store keys

## Behavior

The skill runs nine steps in order. Each step must pass before the next runs.

### Step 1: Pre-flight

- Confirm `supabase` CLI installed. If missing, abort with install instructions.
- Confirm project root has `CLAUDE.md` and `.env.local.example`. If missing, suggest running `mobile-app-scaffold` first.

### Step 2: Initialize the project

```
supabase init
supabase link --project-ref <ref>
```

If no project exists yet, `supabase projects create <name> --region <region>` runs first.

### Step 3: Generate the schema

Read the table list. Render `supabase/migrations/0001_init.sql` from the schema template. Every table gets:

- A UUID primary key
- A `created_at timestamptz default now()`
- A `user_id uuid references auth.users(id)` if the table is user-owned
- RLS enabled
- A policy granting select/insert/update/delete to the row owner

### Step 4: Apply the migration

```
supabase db push
```

### Step 5: Verify table count

This step is non-negotiable. See [references/govihub-postmortem.md](references/govihub-postmortem.md) for the reason.

Run `scripts/verify-tables.ps1`. The script:

1. Counts tables in `public` schema before the migration ran (recorded in step 2).
2. Counts tables after.
3. Compares actual delta to expected delta from the schema file.
4. If counts do not match, dumps the partial state and aborts.

### Step 6: Generate the API contract

Run `scripts/generate-contract.ps1`. Reads the schema. Writes `API_CONTRACT.md` at the project root listing every endpoint the frontend will call.

### Step 7: Configure auth

- `auth.email.enable_confirmations = false` in dev profiles.
- `auth.email.enable_confirmations = true` in production profile.
- Magic-link or OAuth providers configured per the user's choice.

### Step 8: Write keys to .env.local

Append or update these in `.env.local`:

```
EXPO_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=<anon>
SUPABASE_SERVICE_ROLE_KEY=<service-role>
```

If the 1Password CLI (`op`) is installed and the user supplied a vault, write the same keys to a 1Password entry as a backup.

### Step 9: Print the summary

```
Supabase project: <name>
Region:           <region>
Project URL:      https://<ref>.supabase.co
Tables created:   <count>
RLS policies:     <count>
API contract:     ./API_CONTRACT.md
Keys written:     .env.local
1Password entry:  <vault>/<name>-supabase (if used)

Next: run the smoke test once you fill SMOKE_TEST_TOKEN in .env.local.
```

## Hard constraints

- Never skip the table-count verification in step 5.
- Never disable email confirmation in the production profile.
- Never write the service-role key under an `EXPO_PUBLIC_*` prefix.

## Composes with

- Runs after `mobile-app-scaffold`.
- The `API_CONTRACT.md` it produces is read by `security-audit` and `three-tier-test`.
- The `mcp-to-mobile` skill calls this skill automatically.

## References

- [references/rls-patterns.md](references/rls-patterns.md) - common Row Level Security policies.
- [references/schema-patterns.md](references/schema-patterns.md) - schemas for the common AiGNITE app shapes.
- [references/govihub-postmortem.md](references/govihub-postmortem.md) - five-day outage from a silent migration failure.
