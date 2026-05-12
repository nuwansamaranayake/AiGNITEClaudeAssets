# Physical Device Manual Checklist

One-line summary: The checks only real hardware surfaces, run by the user during tier three.

## How to run

The user opens the development build on their physical device by scanning the QR code printed by `scripts/run-tier-three.ps1`. They tick each item below in `TEST_RESULTS.md` as they go.

## Push notifications

- Send a test push notification to the device while the app is foreground. The in-app handler fires.
- Send a test push notification while the app is background. The notification appears in the notification tray.
- Tap the notification while the app is background. The app opens to the correct screen.
- Force-quit the app. Send a notification. Tap it. The app cold-starts to the correct screen.

## Camera

- Open the camera-using screen. The permission prompt appears.
- Deny permission. The app shows a friendly fallback, not a crash.
- Re-enable permission in Settings. Return to the app. The screen recovers.
- Capture an image. The image lands at the expected size and quality.

## Microphone

- Open any audio-recording screen. The mic permission prompt appears.
- Speak, stop, replay. Audio is intelligible.

## Location

- Open a screen needing location. The "Allow Once / Allow While Using / Don't Allow" prompt appears.
- Confirm location accuracy on screen matches the device's actual position within fifty meters.
- Toggle Wi-Fi off and on. Location still resolves over cell data.

## Biometric authentication

- Trigger Face ID or Touch ID. The prompt appears.
- Cancel the prompt. The app shows a passcode fallback.
- Authenticate successfully. The protected screen loads.

## Deep links

- Open the project's email or SMS containing a deep link.
- Tap the link. The app opens to the target screen.
- Tap the link when the app is force-quit. The app cold-starts to the target screen.

## Network resilience

- Toggle airplane mode while a network request is in flight. The app shows a clear error.
- Re-enable network. Retry. The request succeeds.
- Switch from Wi-Fi to cell mid-session. No request errors.

## Performance

- Cold-start the app. Time to first interactive frame is under three seconds.
- Scroll the longest list in the app. No dropped frames.
- Trigger battery saver mode. The app still functions, animations may reduce.

## Display

- Rotate the device. The intended orientation lock holds (most AiGNITE apps lock to portrait).
- Enable Dark Mode in iOS Settings. The app reflects the system preference if intended.
- Use Dynamic Type to bump font size to the largest setting. Text wraps. Nothing clips.

## Privacy

- Take a screenshot of a sensitive screen. If FLAG_SECURE is intended, the screenshot is blocked on Android.
- Switch to the app switcher view on iOS. The screen blurs if intended.

## App installation

- Build and install via TestFlight or internal track. The app icon appears on the home screen.
- The app icon matches the asset at `assets/icon.png`.
- The launch screen matches the asset at `assets/splash.png`.

## Sign-off

After all checks pass, the user types `tier3:PASS` into the prompt. The skill writes the timestamp to `TEST_RESULTS.md`. Any check failed writes `tier3:FAIL` with the failed item names. The skill refuses to mark the build ready.

## What to do when a check fails

A failed check means:

1. Open a bug ticket with the exact failure described.
2. Fix the bug.
3. Re-run all three tiers.

Partial re-runs are not allowed. A fix at tier three may regress tier one. The full sequence runs every time.
