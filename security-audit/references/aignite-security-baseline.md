# AiGNITE Security Baseline

One-line summary: The minimum security posture every AiGNITE product meets before any TestFlight or Play Store submission.

## What this document is

A pass-fail checklist. Every item must be satisfied before the audit returns a green verdict. Items skipped without explicit user override produce a Critical finding.

## Authentication

- All authenticated routes require a valid JWT.
- Email confirmation is enabled in the production Supabase profile.
- Magic-link tokens expire in 600 seconds or less.
- OAuth providers list only callback URLs the project owns.
- Password reset emails go through the verified Resend domain (contact.aigniteconsulting.ai for AiGNITE properties).

## Authorization

- RLS is enabled on every table holding user data.
- No table has a `using (true)` select policy unless the table is explicitly public-read.
- The service role key is never bundled into the client. The scanner enforces this.
- Admin routes check a server-side role check, not a client-supplied flag.

## Secrets management

- No secrets in source. The scanner enforces this with regex patterns for the common formats.
- `.env*` files are in `.gitignore`.
- 1Password vault contains a copy of every production secret. The `supabase-bootstrap` skill writes them on setup.
- Rotation cadence: ninety days for service-role keys, thirty days for any leaked key.

## Network

- HTTPS only. No HTTP in production endpoints. Expo's default network config rejects cleartext.
- CORS allows only the production domains plus the dev origin.
- Webhook endpoints verify signatures (Stripe, Resend, Supabase).

## Data

- PII is stored only in the columns it belongs in. No PII in JSON blobs that get returned to other users.
- Encryption at rest is on for the Supabase project (default for managed Supabase, must check for self-hosted).
- Backups are enabled with at least daily cadence.

## Logging

- No request bodies logged.
- No tokens logged.
- No PII in log messages.
- Logs forward to a managed service with a retention policy under thirty days.

## Mobile-specific

- Deep links validate query parameters before acting.
- Stored sensitive data uses expo-secure-store, not AsyncStorage.
- The app does not embed analytics SDKs that collect PII without the user's consent.
- Sensitive screens disable screenshots on Android via FLAG_SECURE if the app handles payments or health data.

## Rate limiting

- Routes calling paid APIs (OpenAI, Stripe, Resend, Anthropic) have a rate-limit middleware.
- Password reset endpoints are rate-limited to five requests per hour per IP.
- The smoke test verifies the rate limit triggers on the seventh request to a 1-per-minute endpoint.

## Pre-submission gate

The audit produces a green verdict only when:

- Zero Critical findings remain.
- Zero High findings remain unresolved.
- The most recent pass added zero new Critical or High findings.
- The audit document is signed by the project owner.
