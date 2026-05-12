# Screenshot Specification

One-line summary: The screen list and dimensions the submission skill captures.

## Required screens per app

Capture at minimum:

1. Home screen showing the core loop
2. The detail or modal triggered by the core loop action
3. Settings or profile

If the app has more screens, capture up to ten total. Order them by importance, not by navigation order.

## Dimensions

### iOS

| Device class    | Size       | Aspect    |
|-----------------|------------|-----------|
| 6.7" iPhone     | 1290 x 2796 | 9:19.5   |
| 6.5" iPhone     | 1284 x 2778 | 9:19.5   |
| 5.5" iPhone     | 1242 x 2208 | 9:16     |
| 12.9" iPad Pro  | 2048 x 2732 | 3:4      |

### Android

| Device class | Size        | Aspect |
|--------------|-------------|--------|
| Phone        | 1080 x 1920 | 9:16   |
| 7" tablet    | 1200 x 1920 | 9:16   |
| 10" tablet   | 1600 x 2560 | 9:16   |

## Capture method

For iOS: use the running app on iPhone Mirroring, take screenshots through the macOS Screenshot tool, and pipe through the resize step.

For Android: use the emulator's screenshot button or `adb exec-out screencap`.

## Annotation

Each screenshot gets a one-sentence caption rendered in the top safe area. Captions come from the metadata YAML:

```yaml
screenshot_captions:
  - "Track your daily water intake in seconds"
  - "See your streak grow"
  - "Customize your reminders"
```

Caption styling: 16px caption, weight 600, color tokens.text on tokens.surface.

## Naming convention

`store/screenshots/<platform>/<size>/<order>-<screen-name>.png`

Example:
- `store/screenshots/ios/6.7/01-home.png`
- `store/screenshots/ios/6.7/02-detail.png`
- `store/screenshots/ios/6.7/03-settings.png`
