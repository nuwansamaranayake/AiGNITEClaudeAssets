# Apple Submission Checklist

One-line summary: Every requirement Apple enforces on a new TestFlight or App Store submission, with the path the skill writes to satisfy it.

## Metadata

- App name (30 char max)
- Subtitle (30 char max)
- Description (4000 char max)
- Keywords (100 char max total, comma-separated)
- Promotional text (170 char max)
- Primary and secondary category
- Age rating questionnaire
- Copyright (e.g. "© 2026 AiGNITE Consulting LLC")
- Support URL (must resolve to 200)
- Marketing URL (optional but recommended)
- Privacy Policy URL (required if app collects any data)

## Screenshots (required)

- 6.7" iPhone (iPhone 15 Pro Max): 1290 x 2796, minimum 3, max 10
- 6.5" iPhone (older Pro Max): 1284 x 2778, minimum 3, max 10
- 5.5" iPhone: 1242 x 2208, minimum 3, max 10
- 12.9" iPad Pro (if iPad supported): 2048 x 2732

For each size: include the home screen and at least the core loop screen. Annotate with a single sentence in the safe area at the top.

## App icon

- 1024 x 1024 master in `assets/icon.png`
- No alpha channel
- No transparency
- Solid background (Apple rejects transparent icons)

## Privacy nutrition labels

Apple requires explicit declarations for every data type collected:

- Contact info (email, phone): linked to identity?
- Location: precise or coarse?
- Identifiers: device ID, user ID?
- Usage data: analytics?
- Diagnostics: crash data?

The skill reads `store/data-collection.yaml` and fills the App Privacy section. If the YAML is missing, the skill prompts the user to fill it.

## App Review Information

- First name, last name of the AiGNITE contact
- Phone number
- Email address (use the AiGNITE submissions inbox)
- Sign-in required: yes
- Demo account credentials (Supabase test user)
- Notes (e.g. "MCP server backend reached over HTTPS, no special setup needed")

## Export compliance

- Encryption: standard HTTPS only? Answer "No" to the export-compliance question.
- If the app uses non-standard encryption: route to legal.

## Content rights

- Confirm the app does not include third-party trademarks or copyrighted content.
- For AiGNITE products that surface third-party data (FloodPulse, RegScope), include the source attribution in the description.

## Test instructions

If the app needs region-specific data to demo (e.g. Texas highway bids), include a clear path to a region in the reviewer notes. Example: "Open the app, sign in with the demo credentials, tap Texas in the region picker."

## App Store Connect deep link

After `eas submit -p ios` completes, the skill prints the App Store Connect deep link to the new build. The user logs in and taps the final submit button.

## Common rejection reasons (the skill checks each)

- Privacy policy URL missing or broken
- Demo account credentials wrong
- Screenshots in the wrong dimensions
- Description references competitors or platforms not allowed
- App crashes on first launch (covered by three-tier-test)
- App uses private APIs (covered by security-audit)
