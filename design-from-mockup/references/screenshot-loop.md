# Screenshot Loop

One-line summary: How to drive the visual diff loop using Chrome DevTools MCP and what each iteration adjusts.

## The loop in three lines

1. Screenshot the running app.
2. Compare to the reference.
3. Make one targeted change.

Loop until the diff is below tolerance or the user accepts.

## Tooling

Chrome DevTools MCP (tools prefixed `mcp__Claude_in_Chrome__` or via the Claude Preview tools) provides:

- `navigate(url)` to load the Expo web build.
- `screenshot()` to capture the rendered frame.
- `read_page()` to inspect the DOM.
- `javascript_tool()` to read computed styles.

For native screenshots, the iPhone Mirroring + screen capture path works but is slower. Default to the Expo web build for the loop.

## Tolerance bands

- Tight: perceptual diff under 3%. Reserve for marketing-critical screens.
- Moderate: perceptual diff under 8%. Default for most product screens.
- Loose: perceptual diff under 15%. Use for screens behind auth where the visual fidelity matters less than the flow.

The skill picks moderate unless the user overrides.

## What each iteration changes

Each loop iteration must make one targeted change, not a sweeping rewrite. The change is one of:

1. A spacing value (margin, padding, gap).
2. A color value (single hex code adjustment).
3. A border radius value.
4. A font size or weight.
5. A single asset swap.
6. A single shadow tweak.

Sweeping rewrites lose the gains from prior iterations. The skill rejects multi-change iterations.

## How to name a diff

The reasoning each iteration produces a prompt fragment like:

```
Diff observed: the primary button on the home screen has a border radius
of 8 in the build versus 16 in the reference. Adjust theme.radii.primary
to 16. No other changes this iteration.
```

This format makes each iteration auditable. The skill writes every iteration's diff prompt to `design/iterations.log` so the user can trace the path.

## When to stop

Stop the loop when:

- Diff falls below the tolerance threshold.
- Ten iterations have passed without improvement.
- The user types "good enough" or accepts the current frame.
- An iteration would require generating new assets. Stop, regenerate the asset, then resume.

## Common pitfalls

### Looping on the same difference

The model sometimes makes the same change twice without checking. Track the diff prompt across iterations and refuse to apply a change identical to the previous iteration.

### Comparing scales

The reference is a static image. The running app is a live render. Resolution mismatches inflate the diff. Capture the screenshot at the reference's exact dimensions before comparing.

### Comparing platforms

iOS and Android render fonts and shadows differently. The loop should run against one target platform at a time. Default to iOS.

### Forgetting the safe area

iPhone notch and Android nav bar consume vertical space. The screenshot must include or exclude these regions consistently against the reference. The skill checks this and adjusts.
