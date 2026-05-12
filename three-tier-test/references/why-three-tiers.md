# Why Three Tiers

One-line summary: What each tier catches that the others miss, with examples from real AiGNITE projects.

## The premise

A bug found in Chrome costs minutes to fix. A bug found in the simulator costs an hour. A bug found by a user costs a day plus reputation. The three-tier sequence pushes detection as far left as possible without losing the bugs that only the right edge can see.

## Tier one: Chrome (Playwright)

What it catches:

- Console errors thrown during render.
- API calls returning non-2xx.
- Missing imports.
- Broken routing (404 on a known route).
- React warning floods.
- Slow API endpoints (timeouts surface as 0-byte responses).
- Authentication state regressions.

What it misses:

- Touch gestures (pan, pinch, long-press).
- Native modules (camera, biometrics, location).
- Push notifications.
- Layout differences between iOS and Android.
- Status bar overlays.
- Keyboard behavior.

Cost per run: 30 seconds.

## Tier two: Mirror (iPhone Mirroring or Android emulator)

What it catches:

- Layout bugs caused by safe area or status bar.
- Touch target sizes that pass on web but fail on touch.
- Bottom sheet and modal behavior on a small screen.
- Keyboard avoidance on focus.
- Tab bar gesture overlap with the home indicator.
- Font rendering differences.
- Animation timing on a real renderer (web is faster than native).

What it misses:

- Real network conditions (cell signal, 4G fallback).
- Push notifications from production sender ids.
- Real camera permission and hardware quirks.
- Battery and thermal throttling.
- True low-end device performance.
- Biometric prompts.

Cost per run: 5 minutes.

## Tier three: physical device

What it catches:

- Push notifications arriving through APNs and FCM.
- Camera and microphone permission flows.
- Location accuracy on real GPS.
- Biometric prompts and fallback to passcode.
- Battery drain and thermal performance.
- Real font rendering on a Retina or AMOLED display.
- Network resilience on cell vs Wi-Fi.
- Deep links from real Messages or Mail.
- Background fetch behavior.
- App icon installation on the home screen.

What it misses:

- Issues that only surface at scale (race conditions across many users).

Cost per run: 15 minutes.

## Examples from AiGNITE projects

### Beacon GoM

A bug where the alert detail screen crashed if the user opened it during airplane mode. Tier one passed because the test environment had network. Tier two passed because the simulator never went offline. Tier three caught it because the QA engineer toggled airplane mode while reviewing the manual checklist.

### Cosmic Nexus

The push notification handler routed to the wrong screen when the app was cold-started from a notification tap. Tier one and tier two could not test this path. Tier three caught it because the manual checklist includes "cold-start from a push notification".

### FloodPulse

The flood-zone search threw a console error in tier one when the response was an empty array. The frontend assumed at least one result and called `.location` on undefined. Tier one caught it in fifteen seconds. Fixing it took two minutes.

These three examples justify the tier costs. Cheap detection where it works, expensive detection only where it must.

## What happens when a tier is skipped

Skipping tier one means tier two finds the console errors instead, at ten times the cost.

Skipping tier two means tier three finds the layout bugs, at thirty times the cost and on the user's device when they tap your icon.

Skipping tier three means the user finds the push notification routing bug after the App Store review. Recovery time: at minimum a week.

The skill refuses to mark a build ready if any tier is skipped.
