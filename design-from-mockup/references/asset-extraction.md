# Asset Extraction Rules

One-line summary: The one-asset-per-Gemini-call rule and the reasoning behind it.

## The rule

Generate each asset in a separate Gemini Imagegen call. Never request a grid of multiple assets in one call.

## Why grids fail

A grid prompt like "generate four icons on a 2x2 grid with a transparent background" produces:

- Inconsistent transparency across the four cells. One cell ends up with a near-white background that does not key cleanly.
- Variable padding around each subject. Cropping breaks alignment when assets land in the app at different sizes.
- Cross-contamination. The diffusion process bleeds detail from one cell into the next. A water-drop icon picks up a tint from a neighboring leaf icon.
- Composition compromise. The model tries to balance the four subjects across the grid, sacrificing detail in each.

Cropping a grid afterwards looks fine to a human eye but the resulting assets do not match each other in stroke weight, color, or padding.

## Why single-subject calls work

A single-subject prompt tells the model:

- One subject only.
- Transparent background.
- No padding.
- Specific style attributes that carry across the asset set when each call uses the same style block.

The model commits its full capacity to one asset. Backgrounds key cleanly. Padding is consistent. Style is reproducible by reusing the style block.

## The asset extraction prompt template

```
Generate a single icon of {{SUBJECT}}.

Style: {{STYLE_BLOCK}}

Output constraints:
- Transparent background (alpha channel)
- No padding around the subject
- Subject centered in frame
- Square aspect ratio, 1024x1024
- One subject only
- Vector-quality lines

Do not include any text, watermarks, or borders.
```

Reuse `STYLE_BLOCK` verbatim across every asset in a set. Example style block:

```
Rounded geometric icon, two-tone palette using #0B1220 and #4ADE80, soft inner shadow,
2px stroke weight, no fills outside the main shape.
```

## Background validation

After Gemini returns the asset, the skill checks:

1. The image has an alpha channel.
2. The corner pixels have alpha = 0.
3. The bounding box of opaque pixels covers between 60% and 95% of the canvas. Lower means padding. Higher means clipping.

If any check fails, regenerate with a more specific prompt. Do not crop in post.

## Style consistency across a set

When generating a set (e.g. four tab bar icons), keep:

- The same `STYLE_BLOCK` across every call.
- The same canvas dimensions.
- The same model temperature (0.7 for icons, 0.4 for illustrations).

If two icons from the same set look different in stroke or palette, the issue is in the style block, not in cropping. Tighten the style block.

## Anti-pattern from the tutorial

The original tutorial suggested generating a 2x2 grid then asking Claude to crop into individual icons. This approach failed in production because:

- Claude's crop instructions were inconsistent across runs.
- The grid frame leaked into the bottom edge of every cropped icon.
- Two of four icons routinely ended up with the wrong dimensions.

The fix was the one-at-a-time rule. The skill enforces it.
