# GoviHub Post-Mortem: The Five-Day Silent Migration

One-line summary: A migration that reported success but created only half its tables cost GoviHub five days of broken production. This is the reason every AiGNITE migration ends with a table count check.

## What happened

- A migration script defined twenty tables in a single SQL file.
- The Supabase CLI reported the migration succeeded.
- Ten of the twenty tables silently failed to create. The failures were on tables with foreign key references to tables earlier in the same file. A casing issue produced a constraint error per table, but the script kept running.
- The frontend had mock data fallbacks enabled for tables that returned 404 from PostgREST.
- Users saw plausible-looking but fake listings for five days.
- A QA engineer noticed a timestamp from before launch on what should have been a fresh record.

## The five days, hour by hour

Day 1: Migration applied. Smoke test green. Frontend serving mock data for ten tables.

Day 2: Internal team uses the app. Notices nothing because mocks are realistic.

Day 3: First external users sign up. Data they create is stored in tables that do exist. Data they read comes from mocks. They see no difference.

Day 4: Support gets a ticket about "stale data" but the ticket is closed because the page shows new content (still mocks).

Day 5: QA notices the stale timestamp. Investigation finds ten missing tables.

## The fix

Reverted, fixed the casing issue, re-ran the migration. This time with a verification step at the end. Caught two more issues over the next month before they reached users.

## The lesson

Migration tooling reports what it tried to do, not what worked. Real verification means counting tables and comparing to the expected count.

Mock data outside development hides real failures from users and from the team. Errors must be visible.

## Rules baked into supabase-bootstrap

1. After every migration, run `verify-tables.ps1` and compare counts. Abort if the count is off by even one.
2. Generated mobile apps never fall back to mock data outside `NODE_ENV=development`. The fallback is a visible error.
3. The smoke test calls every business endpoint with a real token and verifies a non-empty response. Health checks alone are not enough.
4. The `API_CONTRACT.md` lists every endpoint. Deploys verify the contract matches the live code on both sides.

## How long was the fix worth

Five days of recovered confidence cost roughly thirty minutes of new verification code spread across the migration, smoke test, and audit phases. The trade is permanently good.
