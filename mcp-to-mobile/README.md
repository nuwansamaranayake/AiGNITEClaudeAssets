# mcp-to-mobile

The flagship of the AiGNITE Claude Skills.

## What it does

Takes any AiGNITE MCP server URL and produces a complete React Native consumer mobile app: one screen per public tool, Supabase auth, push notifications, Stripe subscription billing. Converts B2B MCP infrastructure into a B2C revenue product without rebuilding the backend.

## Pipeline

1. Discover tools from the MCP server.
2. Filter to the public-safe whitelist (security boundary).
3. Scaffold the project (calls `mobile-app-scaffold`).
4. Generate one screen per chosen tool.
5. Wire push notifications (alert subscription or ready-notification).
6. Wire Stripe subscriptions (free tier 3 queries/day, paid unlimited).
7. Stand up the database (calls `supabase-bootstrap`).
8. Run security audit (calls `security-audit`).
9. Run three-tier test (calls `three-tier-test`).
10. Offer App Store submission (calls `app-store-submission`).

## When it triggers

Phrases like "turn this MCP into an app", "wrap my MCP server as a mobile app", "build a consumer app for FloodPulse", "MCP to mobile".

## Shortcuts

- `beacon-gom` → Beacon GoM
- `regscope` → RegScope
- `recallwatch` → RecallWatch
- `floodpulse` → FloodPulse
- `airshield` → AirShield
- `cosmic-nexus` → Cosmic Nexus

## Hard rule

Refuses to expose any MCP tool not on the per-server public-safe whitelist. The whitelist is in `references/aignite-mcp-catalog.md`.

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\mcp-to-mobile" `
  -Destination "$env:USERPROFILE\.claude\skills\mcp-to-mobile" -Force
```

## License

See LICENSE at the repo root.
