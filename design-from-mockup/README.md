# design-from-mockup

Part of the AiGNITE Claude Skills.

## What it does

Takes any reference image, mockup, or screenshot and produces a pixel-close mobile UI inside an existing Expo project. Pipeline:

1. Acquire the reference (local image, URL, or generated from a text prompt via gemini-imagegen).
2. Extract assets one at a time (no grid generation).
3. Extract design tokens (palette, fonts, spacing density).
4. Apply assets and tokens to the scaffold.
5. Run a Chrome DevTools screenshot diff loop until the result matches.

## When it triggers

Phrases like "design like this", "match this style", "build from screenshot", "make it look like", "copy this layout".

## Hard rule

Never request multiple assets in a single Gemini call. The one-at-a-time rule is enforced in `references/asset-extraction.md`.

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\design-from-mockup" `
  -Destination "$env:USERPROFILE\.claude\skills\design-from-mockup" -Force
```

## Composes with

Runs after `mobile-app-scaffold`. Uses `gemini-imagegen` for asset generation. Uses Chrome DevTools MCP for the screenshot loop.

## License

See LICENSE at the repo root.
