# higgsfield-media

Generate professional images and videos through the Higgsfield MCP server, driven by Claude Code. Picks the right model for the brief, tracks credit cost, downloads outputs to a structured folder, and hands off to downstream skills for video assembly or document embedding.

Part of the AiGNITE Mobile Development Skills Suite. Built to ship on its own to any Higgsfield Plus subscriber who uses Claude Code.

## What this skill does

- Reads a creative brief in plain language.
- Picks the right Higgsfield model (Soul V2, Nano Banana Pro, Flux 2 Pro, GPT Image 2, Kling 3.0, Seedance 2.0, Veo 3.1, Sora 2, and more).
- Confirms the credit cost before generating anything over the threshold.
- Generates images synchronously and polls video jobs to completion.
- Downloads outputs to `output/YYYY-MM-DD/PROJECT-SLUG/`.
- Writes a `manifest.json` for every project and a global `credit-ledger.csv`.
- Hands off to `remotion-video` for assembled clips or `pptx`/`docx` for deliverables.

## Prerequisites

1. **Higgsfield subscription.** Plus or higher. Free tier does not work because the MCP needs OAuth credentials tied to a paid account.
2. **Claude Code installed.** Get it at https://claude.com/download.
3. **Higgsfield MCP server connected.** One-line install below.

## Install

### Option A: install this skill alone

```powershell
git clone https://github.com/nuwansamaranayake/AiGNITEClaudeAssets.git
cd AiGNITEClaudeAssets
Copy-Item -Recurse "higgsfield-media" -Destination "$env:USERPROFILE\.claude\skills\higgsfield-media" -Force
```

### Option B: install the full AiGNITE suite

```powershell
git clone https://github.com/nuwansamaranayake/AiGNITEClaudeAssets.git
cd AiGNITEClaudeAssets
.\INSTALL.ps1
```

### Connect the Higgsfield MCP

```powershell
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
```

A browser opens for OAuth. Sign in with your Higgsfield account. Return to Claude Code.

Verify:

```powershell
claude mcp list
```

Expect `higgsfield: Connected`.

## Usage examples

### 1. LinkedIn cover series

```
Generate three LinkedIn cover images at 1128x191, dark background, brand mark
centered with generous negative space. Use Nano Banana Pro.
```

The skill picks Nano Banana Pro (best 4K text rendering), prints the cost line (about 6 credits for three images), and generates three variants.

### 2. Product motion clip

```
Create a 5-second product clip for FloodPulse showing the dashboard transitioning
into an aerial view. 16:9 ratio.
```

The skill picks Seedance 2.0 (audio-video sync in one pass), runs the generation, polls for completion, downloads the MP4.

### 3. Full social pack

```
Build a six-asset social pack for the next product release: two square hero images,
two 9:16 short clips, two 16:9 banner stills. Show the credit cost first.
```

The skill prints the cost line, asks for confirmation if total exceeds 100 credits, then generates all six.

### 4. Consistent character UGC series

```
Train a Soul Character from these three reference photos, then generate four
5-second UGC clips of her explaining the product. Use Seedance 2.0 with lip-sync.
```

The skill trains the character once, records the character_id in the project manifest, generates four clips that share the character.

### 5. Budget-capped batch

```
I have 87 credits left. Generate as many product hero shots as that allows on
Nano Banana Pro, white seamless background, three-quarter angle.
```

The skill reads the balance, calculates the safe batch size (preserving the 20-credit floor), and stops at the cap.

## Credit cost honesty

This skill burns your Higgsfield credits. It is not free.

The skill prefers unlimited-tier models (Flux 2 Pro, Seedream 4.5, GPT Image 2, Kling O1 Image) and the free pool (Soul V2, Cinema Studio, Soul Cinema) for iteration. Paid credits go to finals only.

The skill confirms with you before any single generation over 40 credits or any batch over 100 credits. The skill blocks any job that would push your balance below 20 credits without explicit confirmation.

The skill maintains a `credit-ledger.csv` in your workspace tracking every generation. Open it any time to see what you spent.

## Decision matrix preview

| Brief | Model | Why |
|-------|-------|-----|
| Hero image with text on packaging | Nano Banana Pro | Best 4K text rendering, paid ~2 credits |
| Editorial portrait or lifestyle | Soul V2 | Free pool on Plus, magazine-grade |
| Photorealism with a person plus product | GPT Image 2 | Unlimited on Plus |
| Blog hero, illustration | Flux 2 Pro | Unlimited on Plus |
| 5-second product motion | Seedance 2.0 | Audio-video sync, ~9 credits |
| Polished 4K social cut | Kling 3.0 | Camera control, ~6 credits |
| 8-second narrative beat | Veo 3.1 | Long-form coherence, 40 plus credits |
| 15-second cinematic with physics | Sora 2 | Object permanence, 40 plus credits |
| Variant batch for prompt testing | Wan 2.6 | Budget tier |
| Consistent character across shots | Soul Character + any model | Likeness anchored |

Full matrix in [references/model-selection.md](references/model-selection.md).

## Output structure

```
output/
  2026-05-12/
    floodpulse-demo-may/
      images/
        001_nano-banana-pro_4k_2c.png
      videos/
        001_kling-3-0_5s_6c.mp4
      manifest.json
      video-config.yaml
  credit-ledger.csv
```

Filename pattern: `<seq>_<model>_<format>_<credits>c.<ext>`.

## License

MIT. See [LICENSE](../LICENSE) in the repository root.

## Related skills

This skill is part of the AiGNITE Mobile Development Skills Suite. See the [repository README](../README.md) for the full suite.

Hands off cleanly to:

- `remotion-video` for clip assembly with TTS, captions, transitions.
- `docx` and `pptx` for embedding generated assets in deliverables.
- `frontend-design` for hero image generation in web projects.

## Issues and contributions

Open an issue at https://github.com/nuwansamaranayake/AiGNITEClaudeAssets/issues. PRs welcome for additional models, presets, and prompt templates.
