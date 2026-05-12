---
name: mcp-to-mobile
description: Flagship AiGNITE pipeline. Takes any AiGNITE MCP server URL, lists its tools, and scaffolds a complete React Native mobile app with one screen per public tool, Supabase auth, push notifications, and Stripe subscription billing. Converts B2B MCP infrastructure into a B2C consumer product without rebuilding the backend. Use this skill whenever the user mentions turning an MCP into a mobile app, wrapping an MCP as a consumer app, building a mobile front end for an MCP, MCP to mobile, or making a consumer app from an MCP server, even if they do not name the skill by name.
---

# mcp-to-mobile

## Purpose

Convert an existing AiGNITE MCP server into a paid consumer mobile app in one orchestrated pipeline. Compose the other seven skills in the suite into a single command.

## When to trigger

Trigger on these user phrases. Match loosely.

- "turn this MCP into an app"
- "wrap my MCP server as a mobile app"
- "build a consumer app for [MCP name]"
- "mobile front end for [MCP product]"
- "consumer app from MCP"
- "MCP to mobile"

## Inputs to collect

1. MCP server URL, or one of the AiGNITE shortcuts: `beacon-gom`, `regscope`, `recallwatch`, `floodpulse`, `airshield`, `cosmic-nexus`.
2. Target app name (defaults to a derived form).
3. Target bundle ID (defaults to `com.aignite.<slug>`).
4. Whether to include subscription billing (default yes).
5. Whether to include push notifications (default yes for alert-style MCPs, off for request-response).

## Behavior

### Step 1: list tools

- Resolve the shortcut to a URL using [references/aignite-mcp-catalog.md](references/aignite-mcp-catalog.md).
- Call the MCP server's `tools/list` endpoint.
- Print the full tool list.
- Apply the public-safe whitelist for the chosen MCP server. The whitelist lives in the catalog.

### Step 2: select screens

- Show the user the filtered tool list.
- Ask the user to pick which tools become user-facing screens.
- Default to all read-only tools.
- Refuse to expose any tool not on the public-safe whitelist.

### Step 3: scaffold the project

Call `mobile-app-scaffold` with the app name, bundle ID, and MCP URL. The scaffold writes the project tree.

### Step 4: generate screens

For each selected tool, generate one screen at `app/(tabs)/<tool-name>.tsx`. The screen:

- Imports the typed MCP client.
- Renders an input form derived from the tool's `inputSchema`.
- Calls the tool when the user submits.
- Renders the result in a card layout matching the project theme.
- Handles loading, error, and empty states.

See [assets/templates/screen-from-tool.tsx.template](assets/templates/screen-from-tool.tsx.template).

### Step 5: wire push notifications

For alert-style MCPs (FloodPulse, AirShield, RegScope, RecallWatch, Beacon GoM):

- Register the device with Expo Push.
- Subscribe to a topic per the user's choice.
- Display the topic state in Settings.

For request-response MCPs (Cosmic Nexus):

- Register the device with Expo Push.
- Send a notification when the user's report is ready, with a deep link to the report screen.

See [references/push-notification-patterns.md](references/push-notification-patterns.md).

### Step 6: wire Stripe subscriptions

- Free tier: first three queries per day. Hard cap.
- Paid tier: unlimited queries.
- Use the AiGNITE Stripe product templates from [references/stripe-tiers.md](references/stripe-tiers.md).
- Add a paywall component at the third query if the user is on free.

### Step 7: stand up the database

Call `supabase-bootstrap` with the schema:

- `profiles` (user account state)
- `query_log` (rate-limit tracking)
- `subscriptions` (Stripe sync)
- `device_tokens` (push registration)

### Step 8: run the security audit

Call `security-audit`. Refuse to continue if any Critical or High remains.

### Step 9: run the three-tier test

Call `three-tier-test`. Refuse to continue if any tier fails.

### Step 10: offer submission

Print a summary and ask if the user wants to run `app-store-submission` now or later.

## Hard constraints

- Never expose an MCP server's admin or write tools. The skill maintains a public-safe whitelist per AiGNITE MCP and rejects any tool outside the list.
- Never expose the MCP server URL with admin credentials. The mobile client uses the public URL only.
- Never write the service-role Supabase key into the mobile bundle.
- Refuse to ship a consumer app whose query log is not rate-limited.

## Composes with

Calls every other skill in the suite. This is the orchestrator.

## References

- [references/aignite-mcp-catalog.md](references/aignite-mcp-catalog.md) - every AiGNITE MCP, its URL, tools, and public-safe subset.
- [references/mcp-client-patterns.md](references/mcp-client-patterns.md) - calling MCP tools from React Native.
- [references/stripe-tiers.md](references/stripe-tiers.md) - AiGNITE subscription tiers.
- [references/push-notification-patterns.md](references/push-notification-patterns.md) - alert vs ready-notification flows.
