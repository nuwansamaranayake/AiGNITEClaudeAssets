# Push Notification Patterns

One-line summary: Two patterns for AiGNITE MCP-to-mobile apps: alert subscriptions for monitoring products and ready-notifications for request-response products.

## Pattern 1: alert subscriptions

For FloodPulse, AirShield, RegScope, RecallWatch, Beacon GoM.

The user picks topics they care about (e.g. "Harris County floods", "EPA region 6", "USDA recalls"). When the MCP server detects a new event matching a topic, it pushes to every device subscribed to that topic.

### Setup

1. The app registers with Expo Push and stores the token in `device_tokens.token`.
2. The user picks topics in Settings.
3. The selections write to `subscriptions` table with `(user_id, topic)` pairs.
4. The backend cron job watches incoming events and matches them against `subscriptions` rows. For each match, it calls Expo Push with the corresponding device token.

### Notification payload

```json
{
  "to": "ExponentPushToken[xxxx]",
  "title": "Flood Alert: Harris County",
  "body": "Water levels rising at gauge BUFF1. Read more.",
  "data": {
    "topic": "flood:harris-county",
    "deep_link": "floodpulse://alert/abc123"
  }
}
```

### In-app handling

- Foreground: show an in-app banner.
- Background: system displays the notification. Tap deep-links to the alert detail screen.
- Cold start: app reads `Notifications.getLastNotificationResponseAsync()` on launch and navigates if a notification triggered the start.

## Pattern 2: ready-notification

For Cosmic Nexus (and any request-response MCP where the user asks for something that takes minutes).

The user submits a reading request. The MCP server queues the work. When the reading is ready, a push notifies the user.

### Setup

1. The app registers with Expo Push as in pattern 1.
2. When the user submits a reading, the app inserts into `pending_orders` with the device token.
3. The MCP server processes the order. On completion, it inserts into `completed_orders` and triggers a push to the device token.

### Notification payload

```json
{
  "to": "ExponentPushToken[xxxx]",
  "title": "Your full life reading is ready",
  "body": "Tap to view your personalized analysis.",
  "data": {
    "order_id": "abc123",
    "deep_link": "cosmicnexus://reading/abc123"
  }
}
```

### In-app handling

- Foreground: navigate to the reading detail screen with a smooth transition.
- Background: tap routes to the reading detail screen.
- Cold start: same.

## Topic taxonomy

Topics use kebab-case prefixes by domain:

- `flood:<county>` (FloodPulse)
- `air:<facility-id>` (AirShield)
- `recall:<category>` (RecallWatch)
- `reg:<agency>` (RegScope)
- `incident:<operator>` (Beacon GoM)

The topic string is what the backend matches against. The mobile app shows a friendly label to the user.

## Privacy

Push payloads do not contain PII. They contain a topic, an event ID, and a deep link. The detail data is fetched after the user taps the notification, via authenticated MCP calls.

## Cost control

Each push costs nothing through Expo's free tier up to thousands per day. AiGNITE products that exceed the free tier route through APNs and FCM directly. The skill wires both.

## What the skill writes

The skill generates:

1. `services/notifications.ts` wrapping Expo Notifications.
2. `hooks/useDeviceToken.ts` for registration and refresh.
3. A Supabase migration that adds `device_tokens` and `subscriptions` (or `pending_orders` / `completed_orders` for ready-notification apps).
4. A test push button in Settings for verification during tier 3.

## Test path

During tier-3 manual testing, the user:

1. Foreground: triggers a test push from Settings. The in-app banner shows.
2. Background: triggers a test push from Settings. The notification arrives. Tap routes correctly.
3. Cold start: triggers a test push from Settings, force-quits the app, taps the notification. The app cold-starts to the correct screen.

All three checks live in `references/physical-device-checklist.md` of `three-tier-test`.
