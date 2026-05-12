# app-store-submission

Part of the AiGNITE Claude Skills.

## What it does

Runs the EAS Submit pipeline end to end. Generates a privacy policy on contact.aigniteconsulting.ai, produces required screenshots, fills App Store Connect or Google Play metadata, creates the test-reviewer Supabase account, and submits to TestFlight or the Google Play Internal Track.

## When it triggers

Phrases like "submit to App Store", "publish my app", "release to TestFlight", "push to Apple", "Google Play submission".

## Hard rules

- Refuses to start unless `TEST_RESULTS.md` has all three tiers PASS within 72 hours.
- Refuses to start unless `SECURITY_AUDIT.md` is GREEN within 7 days.
- Refuses to submit if the privacy policy URL does not resolve to 200.

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\app-store-submission" `
  -Destination "$env:USERPROFILE\.claude\skills\app-store-submission" -Force
```

## Composes with

Final step after `security-audit` and `three-tier-test`. Called from `mcp-to-mobile`.

## License

See LICENSE at the repo root.
