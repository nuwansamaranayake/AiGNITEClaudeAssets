---
name: design-from-mockup
description: Takes any reference image, mockup, or screenshot and produces a pixel-close mobile UI inside an existing Expo project. Pipeline extracts assets one-at-a-time, removes backgrounds, applies them to the scaffold, then runs a screenshot-diff loop until the result matches. Use this skill whenever the user mentions designing like an existing app, matching a style, building from a screenshot or mockup, copying a layout, or producing a high-end UI from a reference image, even if they do not name the skill by name.
---

# design-from-mockup

## Purpose

Skip the slow manual translation of a mockup into RN components. Drive the asset pipeline and the screenshot diff loop until the running app matches the reference within a tolerable delta.

## When to trigger

Trigger on these user phrases. Match loosely.

- "design like this"
- "match this style"
- "build from screenshot"
- "make it look like"
- "I want this design"
- "use this mockup"
- "copy this layout"
- "design my app to look like"

## Inputs to collect

1. Reference source: local image path, URL, or a text prompt for Gemini Imagegen.
2. Target Expo project path (must exist, with running dev server reachable on http://localhost:8081 or a custom port).
3. Color palette overrides (optional).
4. Match tolerance: tight, moderate, or loose. Defaults to moderate.

## Behavior

### Stage 1: acquire the reference

- If the user passes an image path or URL, save it as `design/reference.png`.
- If the user passes a text prompt, call the `gemini-imagegen` skill with four variations. The user picks one. Save as `design/reference.png`.

### Stage 2: extract assets one at a time

Critical rule: do not request a grid of icons or illustrations from Gemini. Generate each asset in a separate call with the prompt template at `assets/prompts/asset-extraction.txt`.

- Identify discrete assets visible in the reference (icons, illustrations, backgrounds, buttons, logos).
- For each asset, send a separate Gemini call with: "transparent background, no padding, single subject, vector style matching reference."
- Save each asset under `assets/extracted/<name>.png`.
- Validate the asset has a transparent background and a clean edge. Reject if the background bleeds.

See [references/asset-extraction.md](references/asset-extraction.md) for why grid generation fails.

### Stage 3: detect design tokens

- Extract the dominant five-color palette from the reference.
- Identify primary font characteristics (rounded, geometric, serif, monospace).
- Identify spacing density (tight, balanced, generous).
- Write the tokens to `lib/theme.ts` in the project. See [references/design-tokens.md](references/design-tokens.md).

### Stage 4: apply assets to the scaffold

- Place extracted assets at the project's `assets/` folder.
- Update screen components to reference the new assets and the new theme.
- Render the home screen.

### Stage 5: screenshot diff loop

1. Take a screenshot of the running app via Chrome DevTools MCP at the configured port.
2. Compare to `design/reference.png`. Compute a perceptual diff.
3. If the diff is below the tolerance threshold for the chosen match mode, stop.
4. If above, generate a structured prompt naming the specific differences (spacing off by 8px, button radius too sharp, accent color saturation low, etc.) and apply changes.
5. Loop. Max ten iterations or until the user accepts.

See [references/screenshot-loop.md](references/screenshot-loop.md).

## Hard constraints

- Never request multiple assets in a single Gemini call. One asset per call.
- Never proceed past stage 2 with assets that have non-transparent backgrounds.
- Never overwrite the user's `lib/theme.ts` without first writing a backup.

## Composes with

- Runs after `mobile-app-scaffold` produces the project tree.
- Calls `gemini-imagegen` for mockup variations and asset generation.
- Uses Chrome DevTools MCP for the screenshot diff loop.

## References

- [references/asset-extraction.md](references/asset-extraction.md) - the one-at-a-time generation rule and why.
- [references/screenshot-loop.md](references/screenshot-loop.md) - how to use Chrome DevTools MCP for visual verification.
- [references/design-tokens.md](references/design-tokens.md) - AiGNITE default palettes, fonts, and spacing.
