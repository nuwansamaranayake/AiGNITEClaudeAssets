---
name: three-tier-test
description: Enforces the AiGNITE Chrome to mirror to phone testing sequence with hard checkpoints. Tier one runs Playwright over the Expo web build. Tier two runs a recorded walkthrough on iPhone Mirroring or Android emulator. Tier three runs a manual checklist on a physical device. Each tier must pass before the next starts. Use this skill whenever the user mentions testing a mobile app, verifying a build, QA, asking if a build is ready to ship, or running a three-tier test, even if they do not name the skill by name.
---

# three-tier-test

## Purpose

Catch bugs at the layer that surfaces them cheapest. Chrome catches console errors and broken API calls. Mirror catches gesture and layout bugs. Physical device catches sensor, push, and battery bugs.

## When to trigger

Trigger on these user phrases. Match loosely.

- "test my app"
- "verify the build"
- "is this ready to ship"
- "run the test suite"
- "QA the mobile app"
- "three-tier test"
- "pre-flight test"

## Behavior

Run the three tiers in order. Refuse to mark the build "ready" unless all three pass. Each tier writes a pass or fail line to `TEST_RESULTS.md` with a timestamp.

### Tier one: Chrome (Playwright)

1. Start the Expo web build (`npx expo start --web`).
2. Wait for the bundler to settle.
3. Run `scripts/run-tier-one.ps1`. It drives Playwright through every screen.
4. Assert every screen renders without a console error.
5. Assert every API call returns a 2xx status.
6. Hit the same endpoints listed in `scripts/smoke-test.sh`. Reuse the probe list.
7. Write pass or fail to `TEST_RESULTS.md`.

Fails this tier produces an immediate stop. Fix and re-run.

### Tier two: Mirror (iPhone Mirroring or Android emulator)

1. Build a development client (`eas build --profile development --platform <ios|android>`).
2. Install to iPhone Mirroring (Mac) or to the Android emulator.
3. Run `scripts/run-tier-two.ps1`. It loads a Maestro flow or a Detox flow against the running app.
4. Capture screen video for review.
5. Write pass or fail to `TEST_RESULTS.md`.

### Tier three: physical device

1. Generate a QR code for the development build.
2. The user scans with their phone.
3. Run `scripts/run-tier-three.ps1`. It prints a manual checklist.
4. The user ticks items off. The script captures their pass or fail and writes to `TEST_RESULTS.md`.

The physical-device checklist covers the items only real hardware surfaces: push notifications, camera, location, deep links, biometric auth, performance at battery saver, screenshot blocking, app icon installation, and orientation lock.

See [references/physical-device-checklist.md](references/physical-device-checklist.md) for the full list.

## Integration with mobile-app-scaffold

The skill reads the endpoint list from `scripts/smoke-test.sh` produced by `mobile-app-scaffold`. Both must reference the same list. If the smoke test list changes, tier one detects the change at the next run.

## Refusal

The skill refuses to write "READY" to `TEST_RESULTS.md` unless:

- Tier one is a pass.
- Tier two is a pass.
- Tier three is a pass.
- All three passes are within the last seventy-two hours.

## Composes with

- Runs after `security-audit`.
- Runs before `app-store-submission`. The submission skill rejects builds without a recent three-tier pass.

## References

- [references/why-three-tiers.md](references/why-three-tiers.md) - what each tier catches that the others miss.
- [references/playwright-setup.md](references/playwright-setup.md) - wiring Playwright into an Expo web build.
- [references/physical-device-checklist.md](references/physical-device-checklist.md) - the manual checklist for tier three.
