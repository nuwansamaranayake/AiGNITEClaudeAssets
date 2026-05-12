# Google Play Submission Checklist

One-line summary: Every requirement Google enforces on a new Internal Track or Production submission, mirrored to the iOS checklist where the items overlap.

## Metadata

- App name (50 char max)
- Short description (80 char max)
- Full description (4000 char max)
- Category (Apps or Games, then sub-category)
- Tags (up to 5)
- Default language and supported languages
- Contact email (required and public)
- Privacy policy URL (required for all apps)

## Graphic assets

- App icon: 512 x 512, 32-bit PNG with alpha
- Feature graphic: 1024 x 500
- Phone screenshots: at least 2, max 8, 16:9 or 9:16 ratio, min 320px on the short side
- 7-inch tablet screenshots (optional)
- 10-inch tablet screenshots (optional)
- Promo video URL (optional YouTube link)

## Content rating questionnaire

Google's IARC questionnaire covers violence, sexual content, language, controlled substances, gambling, and user-generated content. The skill reads the answers from `store/content-rating.yaml` and submits them via the Google Play Console API.

## Data safety form

For every data type the app collects:

- Is it shared with third parties?
- Is it collected ephemerally or persisted?
- Is collection optional or required?
- Is the data encrypted in transit?
- Can the user request deletion?

The skill reads `store/data-collection.yaml` and submits the form via the Console API.

## Target API level

Google enforces a minimum target SDK level every year. As of 2026, target SDK 35 (Android 15) or higher. The skill checks `app.json` and `android.targetSdkVersion`.

## Permissions

Every permission declared in the manifest needs an in-app justification. Sensitive permissions (location, SMS, call log) trigger an extra review. The skill scans for `dangerous` permissions and prompts for justifications.

## Test reviewer account

- Login credentials in the test instructions block
- Demo region or feature flags pre-configured for the reviewer

## Internal Track first

The skill defaults to the Internal Track for first submissions. Promotion to Production happens manually after the team has tested with internal testers.

## Common rejection reasons (the skill checks each)

- Privacy policy missing
- Data safety form incomplete
- Permission justifications missing
- App targets an outdated SDK
- Screenshots not provided in required sizes
- App crashes on first launch (covered by three-tier-test)
