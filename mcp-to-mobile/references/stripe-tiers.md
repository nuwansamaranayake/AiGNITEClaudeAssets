# AiGNITE Stripe Subscription Tiers

One-line summary: The default subscription product templates the mobile skill wires into every MCP-to-mobile app.

## Tier structure

Every AiGNITE consumer mobile app ships with two tiers:

- Free: limited daily queries. No credit card required.
- Paid: unlimited queries. Single monthly price.

No annual tier in v1. No trial. The free tier is the trial.

## Default price points

| Product       | Daily free queries | Monthly paid price |
|---------------|--------------------|--------------------|
| FloodPulse    | 3                  | $4.99              |
| AirShield     | 3                  | $4.99              |
| RecallWatch   | 3                  | $7.99              |
| Beacon GoM    | 3                  | $9.99              |
| RegScope      | 3                  | $14.99             |
| Cosmic Nexus  | 3                  | $19.99             |

Price points map to perceived value, not cost-to-serve. Cosmic Nexus charges the highest because each reading consumes the most LLM time.

## Stripe product setup

Each AiGNITE Stripe account holds one product per app with one recurring price. The product ID and price ID are stored in:

- `store/stripe-config.yaml` (per project, committed)
- Stripe Dashboard (source of truth)
- 1Password vault for non-committed keys

## In-app purchase strategy

Apple and Google require in-app purchase for digital subscriptions. The mobile app uses:

- iOS: StoreKit via `react-native-iap` configured for auto-renewable subscriptions.
- Android: Google Play Billing via `react-native-iap`.

Server-side webhooks from StoreKit and Google Play sync the user's tier into the `subscriptions` Supabase table. Direct Stripe Checkout is only available on the web admin surface, not in the app, to satisfy store rules.

## Free tier enforcement

The `query_log` table has one row per user per query. RLS limits the user to selecting their own rows. The RPC `check_quota(user_id)` returns the count for today. If the count is at three on a free tier user, the next call returns a quota error.

The paid tier bypasses the quota check by joining `subscriptions` and confirming `tier = 'paid'` and `current_period_end > now()`.

## Paywall component

`assets/templates/subscription-gate.tsx.template` renders the paywall:

- Title and value proposition
- Single CTA: "Upgrade to unlimited"
- Price
- Restore purchases button (required by Apple)
- Terms of service and privacy links

The paywall appears when:

- A free-tier user attempts the fourth query of the day.
- A user taps an explicit Upgrade button in Settings.

## Subscription state in the app

The app reads `subscriptions.tier` on cold start and listens for changes via Supabase Realtime. The UI updates within seconds of a successful purchase or cancellation.

## Refund handling

Refunds processed by Apple or Google trigger a webhook to the AiGNITE backend. The backend sets `tier = 'free'` and `current_period_end = now()`. The app reflects the change on the next Realtime tick.

## What the skill writes

The skill generates:

1. `services/billing.ts` wrapping react-native-iap calls.
2. `components/SubscriptionGate.tsx` rendering the paywall.
3. `lib/quota.ts` with the daily limit check.
4. A Supabase migration that adds the `query_log` table and the `check_quota` RPC.
5. A Stripe product in dashboard with the price point from the table above.
