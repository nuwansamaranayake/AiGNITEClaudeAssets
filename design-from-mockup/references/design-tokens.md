# Design Tokens

One-line summary: AiGNITE default color palettes, font choices, and spacing scales, plus how to derive tokens from a reference image.

## The token shape

Every AiGNITE mobile app exports a single theme module at `lib/theme.ts`:

```typescript
export const theme = {
  colors: {
    bg: '#0B1220',
    surface: '#111827',
    text: '#F3F4F6',
    textMuted: '#9CA3AF',
    primary: '#4ADE80',
    primaryFg: '#0B1220',
    border: '#1F2937',
    danger: '#F87171',
  },
  spacing: { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 },
  radii: { sm: 6, md: 12, lg: 20, pill: 999 },
  typography: {
    h1: { fontSize: 32, fontWeight: '700' },
    h2: { fontSize: 24, fontWeight: '600' },
    body: { fontSize: 16, fontWeight: '400' },
    caption: { fontSize: 12, fontWeight: '400' },
  },
};
```

Every component reads from this module. No hard-coded colors in JSX.

## Default AiGNITE palettes

### Dark default (AiGNITE house style)

- bg `#0B1220`
- surface `#111827`
- primary `#4ADE80`
- text `#F3F4F6`

### Calm light

- bg `#FAFAFA`
- surface `#FFFFFF`
- primary `#6366F1`
- text `#111827`

### High-contrast

- bg `#000000`
- surface `#0F0F0F`
- primary `#FBBF24`
- text `#FFFFFF`

## Extracting tokens from a reference

The skill runs three extractors on `design/reference.png`:

1. Dominant-color extraction. Returns the five most common color clusters. Map to bg, surface, primary, text, accent.
2. Font detection. Apply a heuristic over the rendered text in the image to bucket the typeface as rounded geometric, neo-grotesque, serif, or monospace. Map to the closest open-source font (Inter, Plus Jakarta Sans, Space Grotesk, JetBrains Mono).
3. Spacing density. Measure the gaps between elements relative to the longest dimension. Bucket as tight (gaps below 4%), balanced (4%-7%), or generous (above 7%). Map to the spacing scale.

## Spacing density mapping

- Tight: xs=2, sm=6, md=12, lg=18, xl=24
- Balanced: xs=4, sm=8, md=16, lg=24, xl=32
- Generous: xs=8, sm=12, md=20, lg=32, xl=48

## Radii by aesthetic

- Sharp (corporate, fintech): sm=2, md=4, lg=8
- Soft (consumer, lifestyle): sm=6, md=12, lg=20
- Pill-heavy (gaming, social): sm=8, md=16, lg=24, default pill on buttons

## Anti-pattern: random color picks

Never let the loop pick a color that does not appear in the reference image. The diff prompt is constrained to colors present in the extracted palette. If a new accent color is needed, the skill regenerates the palette from the reference, not from invention.

## Where the tokens live

The skill writes to:

1. `lib/theme.ts` (TypeScript module that components import)
2. `design/tokens.json` (JSON mirror for tooling and audits)
3. `design/iterations.log` (record of every token change during the loop)
