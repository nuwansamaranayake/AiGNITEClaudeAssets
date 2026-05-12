# Remotion Handoff

One-line summary: How `higgsfield-media` writes a `video-config.yaml` that the `remotion-video` skill reads to assemble Higgsfield clips into a final composition with TTS narration and transitions.

## The contract

After Phase 6 (download and organize), if the brief calls for video assembly:

1. `higgsfield-media` writes `video-config.yaml` at the project root referencing downloaded clips by local path.
2. The user (or Claude Code in the same session) invokes `remotion-video`.
3. `remotion-video` reads the YAML, treats each Higgsfield clip as a `screen` or a layer in `src/compositions/scenes/*.tsx`, adds TTS narration, captions, transitions.
4. `remotion-video` renders the final MP4.

Two skills cooperate via a file. Neither calls the other directly.

## video-config.yaml schema

```yaml
project_slug: "floodpulse-demo-may"
title: "FloodPulse May Demo"
duration_seconds: 30
aspect_ratio: "16:9"
fps: 30
output_path: "output/2026-05-12/floodpulse-demo-may/final.mp4"

screens:
  - id: "intro"
    duration: 4
    layers:
      - type: "video"
        source: "videos/001_kling-3-0_5s_6c.mp4"
        fit: "cover"
      - type: "text"
        content: "Houston flood risk in one tap"
        position: "center-bottom"
        style: "headline"
    transition_out: "fade"

  - id: "feature_map"
    duration: 6
    layers:
      - type: "video"
        source: "videos/002_seedance-2-0_5s_9c.mp4"
        fit: "cover"
      - type: "text"
        content: "Real-time gauge data"
        position: "top-left"
        style: "subheading"
    narration: "Real-time gauge data from every monitored creek in Harris County."
    voice: "neural-en-US-male-1"
    transition_out: "slide-left"

  - id: "feature_alerts"
    duration: 6
    layers:
      - type: "image"
        source: "images/001_nano-banana-pro_4k_2c.png"
        fit: "contain"
        background: "#0B1220"
      - type: "text"
        content: "Push alerts before water rises"
        position: "right-center"
        style: "subheading"
    narration: "Push alerts arrive before water reaches your street."
    voice: "neural-en-US-male-1"
    transition_out: "fade"

  - id: "cta"
    duration: 5
    layers:
      - type: "image"
        source: "images/002_nano-banana-pro_4k_2c.png"
        fit: "cover"
      - type: "text"
        content: "Download FloodPulse today"
        position: "center"
        style: "cta"
    narration: "Download FloodPulse from the App Store or Google Play."
    voice: "neural-en-US-male-1"

audio:
  background_music: "assets/audio/calm-tech-bed.mp3"
  background_volume: 0.15

captions:
  enabled: true
  style: "bold-bottom"
  language: "en"
```

## Generation flow

The skill writes a manifest entry per Higgsfield generation, then assembles the `video-config.yaml` by reading the manifest. Sequence:

1. User asks for a 30-second FloodPulse demo with three feature clips and a CTA card.
2. Skill picks Kling 3.0 for the intro motion, Seedance 2.0 for the feature clip with audio, Nano Banana Pro for the alert mock screenshot and CTA card.
3. Skill generates each asset, downloads, updates manifest.
4. Skill assembles `video-config.yaml` mapping each manifest entry to a screen with narration text drawn from the brief.
5. Skill prints the next step:

```
video-config.yaml written.
Next: invoke remotion-video to render. Tell it 'render the video config at video-config.yaml' or 'use the remotion-video skill to render this'.
```

## Mapping rules

| Higgsfield asset | Remotion layer |
|------------------|----------------|
| Video clip | `type: video` |
| 16:9 still | `type: image` with `fit: cover` |
| 1:1 still | `type: image` with `fit: contain` and a colored background |
| 9:16 still | `type: image` with `fit: cover` |

## Narration text generation

The skill drafts narration text from the brief, one sentence per screen. The operator reviews the YAML before invoking `remotion-video`. The Remotion skill regenerates the narration audio via its existing TTS pipeline.

## When not to write video-config.yaml

If the brief produces standalone deliverables (separate clips for different campaigns), do not write a single config. Each clip stands on its own. The `manifest.json` lists them; downstream usage decides what to do.

## Pitfalls

- Aspect ratio mismatch: if Higgsfield clips are 9:16 and the Remotion composition is 16:9, the skill must call out the mismatch in the YAML comment block at the top so the operator does not ship a letterboxed render by accident.
- Frame rate mismatch: Higgsfield typically renders at 24 or 30 fps. The YAML inherits the higher fps and Remotion resamples.
- Duration mismatch: if the sum of screen durations exceeds the requested total, the skill trims the final screen and notes it in the YAML comment block.
