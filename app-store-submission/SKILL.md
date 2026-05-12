---
name: app-store-submission
description: Runs the AiGNITE EAS Submit pipeline end to end. Generates privacy policies hosted on contact.aigniteconsulting.ai, produces required screenshots, fills App Store Connect or Google Play metadata from a YAML config, creates the test-reviewer account, and submits to TestFlight or Internal Track. Use this skill whenever the user mentions submitting to the App Store, publishing an app, releasing to TestFlight, pushing to Apple, Google Play submission, or EAS submit, even if they do not name the skill by name.
---

# app-store-submission

## Purpose

Take a verified build from "ready to ship" to "uploaded to store with reviewer credentials, metadata, screenshots, and policy URLs filled out." Stop at the human-required final tap.

## When to trigger

Trigger on these user phrases. Match loosely.

- "submit to App Store"
- "publish my app"
- "release to TestFlight"
- "push to Apple"
- "Google Play submission"
- "EAS submit"
- "ship it"

## Pre-flight refusals

The skill refuses to start unless:

- `TEST_RESULTS.md` shows tier one, two, and three PASS within the last seventy-two hours.
- `SECURITY_AUDIT.md` shows a GREEN verdict within the last seven days.
- `app.json` has a valid bundle ID, version, and icon path.
- `eas.json` has a production profile.

If any check fails, the skill names the failed item and exits.

## Inputs to collect

1. Target platform: `ios`, `android`, or `both`.
2. Distribution channel: `testflight` or `production` (iOS), `internal` or `production` (Android).
3. App Store Connect metadata YAML path (defaults to `store/app-store-metadata.yaml`).
4. Privacy policy URL slug (defaults to project slug).
5. Test reviewer credentials (existing or generate new).

## Behavior

### Step 1: privacy policy

- Read or generate `store/privacy-policy.md` from the template.
- Push it to `contact.aigniteconsulting.ai/privacy/<slug>.html`.
- Record the URL in metadata.

### Step 2: support page

- Read or generate `store/support.md` from the template.
- Push it to `contact.aigniteconsulting.ai/support/<slug>.html`.
- Record the URL in metadata.

### Step 3: build

- Run `eas build --profile production --platform <target>`.
- Wait for the build to finish.
- Cache the build artifact URL.

### Step 4: screenshots

- Run the running app on iPhone Mirroring (or the Android emulator).
- Capture screenshots in every required size:
  - iOS: 6.7" (1290x2796), 6.5" (1284x2778), 5.5" (1242x2208), iPad 12.9" (2048x2732)
  - Android: phone (1080x1920) and tablet (1200x1920)
- Save to `store/screenshots/<platform>/<size>/<screen-name>.png`.
- Annotate each with a short caption matching the metadata YAML.

### Step 5: metadata

- Read `store/app-store-metadata.yaml`.
- Required fields: name, subtitle, description (4000 chars max iOS, 4000 Android), keywords (100 chars iOS), category, age rating, contact email, support URL, privacy URL.

### Step 6: test reviewer account

- Check if a reviewer user exists in Supabase. If not, create one with a known email and password.
- Add the credentials to the App Review Information block.

### Step 7: submit

- Run `eas submit --platform <target>`.
- Wait for the upload to complete.
- Print the App Store Connect or Google Play Console deep link.
- Prompt the user to log in and tap the final submit button.

## Hard constraints

- Refuse to submit without a recent three-tier test PASS.
- Refuse to submit without a recent security audit GREEN.
- Privacy policy and support URLs must resolve to 200 before submission.
- Reviewer credentials must work against the production Supabase project.

## Composes with

- Runs after `three-tier-test` and `security-audit`.
- Final step in the `mcp-to-mobile` pipeline.

## References

- [references/apple-checklist.md](references/apple-checklist.md) - Apple submission requirements.
- [references/google-checklist.md](references/google-checklist.md) - Google Play requirements.
- [references/privacy-policy-template.md](references/privacy-policy-template.md) - AiGNITE standard privacy language.
