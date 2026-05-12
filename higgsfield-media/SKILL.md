---
name: higgsfield-media
description: Generate professional images and videos using the Higgsfield MCP server. Supports 30 plus models including Soul V2, Nano Banana Pro, GPT Image 2, Flux 2 Pro, Seedream 4.5, Seedream 5.0 Lite, Kling 3.0, Seedance 2.0, Veo 3.1, and Sora 2. Use this skill whenever the user wants to generate an image, generate a video, create an ad creative, make a product photo, make a UGC video, build a social pack, create a LinkedIn cover, design a hero image, build a newsletter header, design a blog hero, produce architecture-diagram backdrops, or generate any visual asset where Higgsfield is appropriate. Triggers also fire on phrases like use Higgsfield, with Kling, with Veo, with Sora, with Seedance, Nano Banana, Soul V2, Soul Character, Flux 2, GPT Image, Marketing Studio, ad pack, social pack, 5-second clip, 15-second video, cinematic ad, product hero shot, lifestyle photo, reel, TikTok video, YouTube short, AI image, AI video, Instagram reel. Use even if the user does not name Higgsfield. Requires an active Higgsfield subscription and the Higgsfield MCP server connected via claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp.
license: MIT
---

# higgsfield-media

## Purpose

Turn a creative brief into a finished image or video asset (or a coordinated set of assets) using the right Higgsfield model for the job, at the right credit cost, with the output saved to disk and a manifest written for downstream skills to consume.

## Preflight check

Run before every brief.

1. Verify Higgsfield MCP is connected. Run `scripts/check-mcp.ps1`. If the script exits non-zero, print the one-line install command and stop:

```
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
```

2. Verify credit balance. Run `scripts/check-balance.ps1`. Block if balance is below 50 credits and the planned batch will overrun.

## Behavior: seven phases

The skill runs in seven phases. Skip a phase only when the user says so.

### Phase 1: Preflight

MCP connected. Balance fetched. Credit ledger read for the current month.

### Phase 2: Brief intake

Read the user's request. Extract:

- Asset type (image, video, multi-asset pack)
- Quantity (single, batch of N, full pack)
- Aspect ratio (1:1, 16:9, 9:16, 4:5)
- Output usage (LinkedIn, Instagram, blog hero, ad, internal slide)
- Subject (product, person, scene, abstract)
- Style cues (cinematic, flat lay, lifestyle, editorial, illustration)
- Text requirement (any copy that must render legibly)
- Character consistency requirement
- Budget cap if specified

Ask at most three pointed questions for missing fields. Default to sensible choices when in doubt.

### Phase 3: Model selection

Apply the decision matrix in [references/model-selection.md](references/model-selection.md). Prefer unlimited models for iteration. Reserve paid credits for the final render. Print the selected model and the cost estimate before generating.

### Phase 4: Cost confirmation

Compute projected credits for the full batch. Print one line:

```
model=<slug> count=<N> credits/unit=<X> total=<Y> percent_of_monthly=<Z>%
```

Require explicit yes from the user for any single generation over 40 credits or any batch over 100 credits total. Smaller jobs proceed without asking.

### Phase 5: Generation

Call the Higgsfield MCP tool. Image jobs return a URL synchronously. Video jobs return a job handle; poll `get_generation_status` every 8 seconds. Cap polling at 5 minutes. On timeout, surface the job handle and stop polling.

### Phase 6: Download and organize

Download every URL to a structured output tree:

```
output/
  YYYY-MM-DD/
    PROJECT-SLUG/
      images/
        001_nano-banana-pro_4k_2c.png
      videos/
        001_kling-3-0_5s_6c.mp4
      manifest.json
```

Filename pattern: `<seq>_<model-slug>_<format-hint>_<credits>c.<ext>`. Write `manifest.json` incrementally after every generation so a crash mid-batch leaves a readable record. Schema in [references/manifest-schema.md] if you split it out, otherwise inline in this section.

Manifest fields per generation: seq, type, model, prompt, params, credits, url, local_path, duration_seconds, status.

Top-level fields: project_slug, brief, started_at, balance_before, balance_after, generations.

Append a row to `output/credit-ledger.csv` for every generation: timestamp, project, model, credits, balance_after.

### Phase 7: Handoff

If the brief calls for video assembly, write `video-config.yaml` referencing the downloaded clips and pass control to `remotion-video`. See [references/remotion-handoff.md](references/remotion-handoff.md).

If the brief calls for a document or pitch deck, hand off to `docx` or `pptx` with the image paths.

## Decision matrix preview

Full matrix in [references/model-selection.md](references/model-selection.md). Quick reference:

| Brief looks like | Model | Why |
|------------------|-------|-----|
| Hero image with text on packaging | Nano Banana Pro | Best 4K text rendering |
| Editorial portrait, fashion, Sri Lankan e-commerce | Soul V2 | Free pool, editorial quality |
| Photorealism with a person holding a product | GPT Image 2 | Unlimited on Plus |
| Blog hero, illustration, AEO insight cover | Flux 2 Pro | Unlimited on Plus |
| Concept diagram or abstract idea | Seedream 5.0 Lite | Visual reasoning, unlimited |
| Architecture diagram backdrop | Seedream 4.5 | High resolution, unlimited |
| 5-second product motion clip | Seedance 2.0 | Audio-video sync, ~9 credits |
| Polished 4K social cut | Kling 3.0 | Camera language, ~6 credits |
| 8-second narrative beat | Veo 3.1 | Long-form coherence, 40 plus credits |
| 15-second cinematic ad with physics | Sora 2 | Object permanence, 40 plus credits |
| Variant batch for prompt testing | Wan 2.6 or Kling 2.5 Turbo | Budget tier |
| UGC talking head | Seedance 2.0 with lip-sync | Single pass |
| Consistent character across multiple shots | Soul Character then any model | Character ID persists |

## Credit cost summary

Approximate, verify current numbers in [references/credit-costs.md](references/credit-costs.md).

| Tier | Models | Cost |
|------|--------|------|
| Unlimited on Plus | Flux 2 Pro, Seedream 4.5, Seedream 5.0 Lite, GPT Image 2, Kling O1 Image, Nano Banana 2 (2K) | 0 credits |
| Free pool (5,000 monthly) | Soul V2, Cinema Studio, Soul Cinema | 0 credits until pool exhausted |
| Light paid | Nano Banana Pro | ~2 per image |
| Mid paid video | Kling 3.0, Wan 2.6, Hailuo 02 | 5 to 6 per clip |
| Heavy paid video | Seedance 2.0 | ~9 per clip |
| Premium paid video | Veo 3.1, Sora 2 | 40 to 70 per clip |

## Output folder structure

Every project gets its own folder under `output/YYYY-MM-DD/PROJECT-SLUG/`. `manifest.json` is the source of truth. `output/credit-ledger.csv` aggregates spend across all projects.

## Engineering standards (non-negotiable)

1. Root-cause fixes only. Read MCP error payloads. No frontend patches when the MCP returns errors.
2. Smoke tests verify real generation. A 1-credit Flux 2 Pro probe with file download is the smoke test, not a `claude mcp list` health check.
3. No silent fallbacks. If Higgsfield errors, surface it. Never substitute another provider without explicit user opt-in.
4. Verify credit balance before any batch over 50 credits.
5. Maintain `manifest.json` per project and `credit-ledger.csv` across the workspace.
6. Confirm with the user before any single generation over 40 credits or any batch over 100 credits.

## Hard constraints

- Never queue a job that would push balance below 20 credits without explicit confirmation.
- Never silently fall back to another provider on Higgsfield error.
- Never proceed past Phase 4 without printing the cost line.

## Composes with

- Runs alongside `mobile-app-scaffold` for App Store screenshot generation.
- Hands off to `remotion-video` for clip assembly with TTS.
- Hands off to `docx` and `pptx` for asset embedding in deliverables.
- Hands off to `frontend-design` for hero image generation in web projects.

## References

- [references/model-selection.md](references/model-selection.md) - full decision matrix with worked examples.
- [references/credit-costs.md](references/credit-costs.md) - current credit prices, last-verified date.
- [references/marketing-studio-presets.md](references/marketing-studio-presets.md) - the canned modes.
- [references/prompting-cookbook.md](references/prompting-cookbook.md) - model-specific prompt tips.
- [references/soul-character-workflow.md](references/soul-character-workflow.md) - character training and reuse.
- [references/remotion-handoff.md](references/remotion-handoff.md) - video-config.yaml format.
- [references/troubleshooting.md](references/troubleshooting.md) - OAuth, timeouts, rate limits, model-not-found.
