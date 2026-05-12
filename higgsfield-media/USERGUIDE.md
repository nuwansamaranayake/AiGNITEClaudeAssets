# higgsfield-media User's Guide

A practical walkthrough for using the `higgsfield-media` skill from your first generation to multi-asset campaigns. Read this start to finish the first time. Bookmark the workflow sections after.

## Table of contents

1. [Before you start](#1-before-you-start)
2. [Install in five minutes](#2-install-in-five-minutes)
3. [Connect and authenticate](#3-connect-and-authenticate)
4. [Your first generation](#4-your-first-generation-the-smoke-test)
5. [Reading the cost line](#5-reading-the-cost-line)
6. [Common workflows](#6-common-workflows)
7. [Working with multiple variants](#7-working-with-multiple-variants)
8. [Consistent characters across shots](#8-consistent-characters-across-shots)
9. [Handing off to remotion-video](#9-handing-off-to-remotion-video)
10. [Managing your monthly credits](#10-managing-your-monthly-credits)
11. [Where your files live](#11-where-your-files-live)
12. [Common problems and fixes](#12-common-problems-and-fixes)
13. [Tips that compound](#13-tips-that-compound)

---

## 1. Before you start

You need three things:

1. **A Higgsfield subscription.** Plus or higher. The free tier does not work because the MCP server needs OAuth credentials tied to a paid account. Plus is $39 per month annual and gives you 1,000 monthly credits plus unlimited access to several models.
2. **Claude Code installed.** Download from https://claude.com/download. Sign in.
3. **A working directory** where you want your generated assets to land. Most operators use a single shared workspace and let the skill organize by date and project.

Pricing reality: the skill burns your Higgsfield credits. It does not call paid APIs on your behalf outside Higgsfield. Unlimited-tier models (Flux 2 Pro, GPT Image 2, Seedream 4.5, Seedream 5.0 Lite, Kling O1 Image) cost zero credits on Plus. Paid models burn between 1 and 70 credits per generation depending on the tier.

## 2. Install in five minutes

Open PowerShell:

```powershell
git clone https://github.com/nuwansamaranayake/AiGNITEClaudeAssets.git
cd AiGNITEClaudeAssets
Copy-Item -Recurse "higgsfield-media" -Destination "$env:USERPROFILE\.claude\skills\higgsfield-media" -Force
```

Or install the full AiGNITE Claude Skills collection:

```powershell
.\INSTALL.ps1
```

Either way, the skill lives at `$env:USERPROFILE\.claude\skills\higgsfield-media\` and loads automatically in every Claude Code session.

## 3. Connect and authenticate

The skill talks to Higgsfield through the official hosted MCP server. Register it once with Claude Code:

```powershell
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
```

Then open Claude Code and ask:

> Please authenticate with Higgsfield.

Claude calls the `authenticate` tool, prints an OAuth URL, and waits. Open the URL in your browser, sign in with your Higgsfield Plus account, and approve the access request. The browser lands on a localhost callback page that says "Authentication Successful". Return to Claude Code.

Verify the connection:

```powershell
claude mcp list
```

Look for `higgsfield: connected`. Inside Claude Code, ask:

> What is my Higgsfield credit balance?

You should see something like `{"credits":1010,"subscription_plan_type":"plus"}`. If you do, you are ready.

If you have multiple workspaces (team plus personal), ask Claude to list them and select the one you want as the default target. The skill will not switch workspaces silently.

## 4. Your first generation: the smoke test

Run this exact prompt the first time. It costs one credit and validates the entire pipeline from auth to file download.

> Run the higgsfield-media smoke test.

The skill will:

1. Verify the MCP connection.
2. Check your balance.
3. Generate a 1024x1024 abstract image with Flux 2 Pro (unlimited tier, 1 credit).
4. Download the PNG to `output/2026-05-12/smoke-test/images/001_flux-2-pro_1k_1c.png`.
5. Write a `manifest.json` with the full generation record.
6. Append a row to `output/credit-ledger.csv`.
7. Verify the file is a real PNG over 10KB.

If all seven steps pass, the pipeline is green. You will see a result like:

```
Smoke test passed.
File: 2026-05-12/smoke-test/images/001_flux-2-pro_1k_1c.png
Size: 1,070,986 bytes
Balance: 1010 -> 1009 credits
```

If any step fails, the skill names the failure and the fix.

## 5. Reading the cost line

Before any generation over the free thresholds, the skill prints a one-line cost summary:

```
model=nano_banana_pro count=3 credits/unit=2 total=6 percent_of_monthly=0.6%
```

This means: three Nano Banana Pro images, two credits each, six credits total, which is 0.6 percent of your 1,000 monthly allocation.

Confirmation rules:

- Under 40 credits per generation and under 100 credits total: proceeds without asking.
- Single generation over 40 credits (e.g. Veo 3.1, Sora 2): pauses and asks for explicit yes.
- Batch over 100 credits total: pauses and asks for explicit yes.
- Would push balance below 20 credits: pauses regardless of size.

The 20-credit floor preserves emergency capacity. The skill will not silently burn through your reserve.

## 6. Common workflows

### LinkedIn cover image

> Generate three LinkedIn cover images, 1128x191, dark navy background with the green and red yin-yang AiGNITE motif, three different compositional variations. Use Nano Banana Pro.

What happens:

- Model: Nano Banana Pro (best 4K text rendering, ~2 credits each).
- Cost: 6 credits total, no confirmation needed.
- Aspect ratio: 1128x191 banner crop. The skill embeds this in the prompt and the parameter.
- Output: three PNGs in `output/2026-05-12/aignite-linkedin-cover/images/`.
- Variations: composition descriptors differ across the three prompts; subject, palette, and style stay constant.

Use the result in LinkedIn's banner upload. The dimensions are exact.

### Product hero shot

> Create a product hero shot for DrapeStudio: a thirty-year-old Sri Lankan woman in a deep emerald silk saree with gold border, against a cream Galle Fort wall at golden hour, 4:5 aspect ratio. Editorial fashion style.

What happens:

- Model: Soul V2 (free pool on Plus, editorial quality).
- Cost: 0 credits (within the 5,000 monthly free pool).
- Aspect ratio: 4:5 for portrait feed posts.
- Output: one PNG, downloaded and recorded.

If the same brief calls for product copy on packaging, the skill switches to Nano Banana Pro instead.

### Blog hero image

> Make a blog hero for an AEO insight page on query intent. Flat vector illustration, isometric, prism splitting a beam of light into AI engine names, indigo and emerald palette, 16:9.

What happens:

- Model: Flux 2 Pro (unlimited on Plus, faithful style adherence).
- Cost: 0 credits.
- Aspect ratio: 16:9 for blog headers.
- Output: one PNG ready to drop into your CMS or Remotion screen.

### 5-second product motion clip

> Create a 5-second product motion clip for FloodPulse showing the dashboard fading into a Houston neighborhood aerial. 16:9 ratio. Use Seedance 2.0 so we get audio sync in one pass.

What happens:

- Model: Seedance 2.0 (9 credits, audio-video sync).
- Cost: 9 credits, no confirmation needed.
- Polling: video jobs run async. The skill polls every 8 seconds for up to 5 minutes.
- Output: one MP4 in `output/2026-05-12/floodpulse-demo/videos/001_seedance-2-0_5s_9c.mp4`.
- Manifest entry includes the job ID for re-display later.

### 15-second cinematic ad with physics

> Build a 15-second cinematic ad for Cosmic Nexus. A glass bottle with a swirling galaxy inside falls in slow motion, shatters on a wood floor, and the galaxy reforms midair as a Vedic mandala. Use Sora 2.

What happens:

- Model: Sora 2 (40-70 credits, physics and object permanence).
- Cost: 50 to 60 credits typical. Skill pauses for confirmation because cost is over 40 per generation.
- You say yes. Generation runs for 2-3 minutes.
- Output: one 15-second MP4.

This is the most expensive single generation in your toolkit. Reserve it for hero ads.

### UGC talking head

> Generate a UGC clip of a thirty-five-year-old woman with warm features saying: "I checked my Vedic chart this morning and the career section actually matched what happened today at work." Setting: sunlit home office. 9:16 ratio.

What happens:

- Model: Seedance 2.0 with lip-sync (9 credits).
- Aspect ratio: 9:16 for Reels.
- Output: one MP4 with the quoted line spoken on camera.

For a four-clip UGC series with the same person, train a Soul Character first (see section 8) and reuse the character ID across all four prompts.

### Architecture diagram backdrop

> Generate a clean modern data center server hallway backdrop for a pitch deck. No people, no readable text on equipment, cool blue overhead LED at 5500K, 35mm wide-angle, 16:9.

What happens:

- Model: Seedream 4.5 (unlimited on Plus, high-resolution detail).
- Cost: 0 credits.
- Output: one PNG ready to drop into Keynote or PPTX as a slide background.

## 7. Working with multiple variants

When you need a few options to pick from, ask for them in one brief:

> Generate four LinkedIn cover variations for AiGNITE Consulting. Same dark navy background and yin-yang motif. Each variation should change the compositional descriptor: centered, off-center left with copy space right, layered with subtle depth, and minimalist with a single accent line.

The skill writes one prompt per variation, runs them in parallel up to the Plus parallel cap (8 image jobs), downloads each, and shows them side by side.

Tips:

- Keep the style block identical across variations. Change only the composition or camera descriptor.
- Variants under 8 total run in one batch. Above 8, the skill chunks automatically.
- For very different styles, run separate generations rather than variations.

## 8. Consistent characters across shots

If you need the same person across more than two shots (e.g. a four-clip UGC series), train a Soul Character once:

> Train a Soul Character from these three reference photos for my Cosmic Nexus spokesperson. The character is a thirty-five-year-old woman with warm features and shoulder-length dark hair, professional context.

Provide 3 to 5 reference photos. The training pass takes 3-5 minutes and burns a small number of credits. The skill records the `character_id` in the project manifest.

Then for each downstream clip:

> Generate a 5-second UGC clip with the Cosmic Nexus spokesperson character. She says: "Today's hora is exceptional for new beginnings." Setting: sunlit home office. Mood: warm and confident.

The skill reads the character ID from the manifest and passes it to Seedance 2.0. The face stays consistent across every clip.

Anti-patterns to avoid:

- Training on reference photos with multiple people in them. Crop to one person first.
- Training on heavy-filter photos. Use natural photos.
- Reusing the same character across very different stylistic models (e.g. Soul V2 portraits and Flux 2 illustration). Stick to one stylistic family per character.

Full guide: [references/soul-character-workflow.md](references/soul-character-workflow.md).

## 9. Handing off to remotion-video

After generating clip-level assets, ask the skill to write a Remotion configuration:

> Now write a video-config.yaml for remotion-video that uses the three FloodPulse clips and a CTA card, with TTS narration over each. The full composition should be 30 seconds, 16:9, ending on "Download FloodPulse today".

The skill writes `video-config.yaml` at the project root referencing each downloaded clip by local path. The file includes:

- One `screen` per clip with duration, layers (video, text, image), and transitions.
- A narration line per screen for the TTS pipeline.
- A background music slot (empty by default).
- Captions enabled.

Then invoke `remotion-video`:

> Use the remotion-video skill to render the video-config.yaml.

Remotion reads the YAML, generates TTS audio from each narration line, layers text and transitions over the Higgsfield clips, and renders the final MP4.

The two skills do not call each other directly. The contract is the YAML file. Edit the narration, music, and captions before rendering if needed.

## 10. Managing your monthly credits

The skill tracks every generation in two places:

- **Per-project manifest** at `output/<date>/<project>/manifest.json`. Includes the full prompt, parameters, credit cost, URL, local path, and timestamp for every generation in the project.
- **Global credit ledger** at `output/credit-ledger.csv`. One row per generation across all projects. Columns: timestamp, project, model, type, credits, balance_after, prompt_hash, local_path.

Check spend at any time:

> Show me my Higgsfield credit ledger.

Or:

> How many credits have I spent this month?

The skill reads the ledger and sums by current calendar month.

Budget hygiene rules the skill follows automatically:

- Warn if cumulative monthly spend exceeds 800 credits (80 percent of allocation).
- Block any job that would push balance below 20 credits without explicit confirmation.
- Prefer unlimited-tier models for iteration. Reserve paid credits for finals.
- Refuse to start a batch over 50 credits without verifying current balance first.

You can also ask for a transaction report direct from Higgsfield:

> Show me my Higgsfield transactions for this month.

This pulls from the `transactions` tool and shows every credit movement at the source of truth.

## 11. Where your files live

Default directory structure:

```
output/
  2026-05-12/
    floodpulse-demo-may/
      images/
        001_nano-banana-pro_4k_2c.png
        002_nano-banana-pro_4k_2c.png
      videos/
        001_seedance-2-0_5s_9c.mp4
      manifest.json
      video-config.yaml
  2026-05-13/
    cosmic-nexus-ugc/
      videos/
        001_seedance-2-0_5s_9c.mp4
        002_seedance-2-0_5s_9c.mp4
      manifest.json
  credit-ledger.csv
```

Filename pattern: `<seq>_<model>_<format>_<credits>c.<ext>`.

The CDN URLs Higgsfield returns are pre-signed and expire after about 7 days. The skill downloads to local disk immediately to keep your assets reachable indefinitely.

If you need to re-display a past generation in the Higgsfield UI, ask:

> Show me job IDs <id1>, <id2> in the Higgsfield widget.

The skill calls `job_display` and the widget renders them.

## 12. Common problems and fixes

### "OAuth token expired"

The Higgsfield session expired. Re-authenticate:

> Please re-authenticate with Higgsfield.

The skill calls `authenticate` and prints a new URL. Sign in again.

### "Model not found"

The model slug in your request does not match a live model ID. The skill catches this and offers the closest match. If the issue persists, ask:

> Search Higgsfield for models matching "flux".

This calls `models_explore` with the right action and prints the live IDs.

### "Video job stuck past 5 minutes"

Some video generations exceed the polling cap. The skill surfaces the job handle and stops polling. Check status later:

> Check the status of Higgsfield job <id>.

If the job completes, the skill downloads it and adds it to the manifest. If it fails, the skill records the error and refunds the credits where applicable.

### "Parallel job cap exceeded"

Plus caps at 8 parallel image jobs and 6 parallel video jobs. For batches above the cap, the skill chunks automatically. You see a message like "Chunking 12 images into 2 batches of 8 and 4."

### "Insufficient credits"

The skill blocks any job that would push balance below 20 credits unless you confirm. If you hit a real "insufficient credits" error mid-batch, the skill writes a partial manifest with `status: aborted-low-balance` and stops. Top up the plan or wait for monthly refresh.

### "Generation quality is lower than expected"

Check three things:

1. Did you use the right model for the brief? See the decision matrix in [references/model-selection.md](references/model-selection.md).
2. Did you write the prompt the way the model likes? See [references/prompting-cookbook.md](references/prompting-cookbook.md).
3. Did the model produce a fallback (e.g. defaulted resolution to 1k when you wanted 2k)? Read the `adjustments` block in the response.

### "The skill triggered on something I did not want generated"

The skill description matches phrases like "generate an image" and "create a video". If you said "find me a stock photo" the skill should not trigger; the description excludes plain "image" without a generation verb. If it did, tell Claude:

> I do not want to generate this. I want to search.

Claude steps out of the skill and uses a search tool instead.

## 13. Tips that compound

**Use Wan 2.6 or Kling 2.5 Turbo for prompt iteration.** Burning Veo 3.1 or Sora 2 credits on first-draft prompts is the fastest way to exhaust your monthly allocation.

**Reuse style blocks across a campaign.** If you generate a logo with a style block, reuse the exact same style descriptor on all related assets. Visual identity holds together.

**Name your projects with date and intent.** `aignite-linkedin-cover-q2`, `floodpulse-demo-may`, `cosmic-nexus-ugc-vol1`. Future you reading the manifest will thank you.

**Run the smoke test on the first of every month.** Five seconds, one credit, validates the auth and pipeline before you commit to a real production batch.

**Tell Claude the intent, not just the model.** "Build a hero image with text rendering" beats "use Nano Banana Pro". The skill picks the right model when you describe the intent.

**Set a budget cap when you have one.** "I have 87 credits left, generate as many product shots as fits" lets the skill stop at the limit automatically.

**Keep the asset folder under version control with a tight gitignore.** Commit the `manifest.json` and the smaller proofs. Gitignore the large MP4s and full-res PNGs unless you want them in history.

**Use the virality predictor on every ad clip.** The `virality_predictor` tool scores engagement risk before you ship. It is part of the same MCP. Ask:

> Predict virality on this clip.

The skill passes the local path to the tool and prints the score breakdown.

---

For deeper technical detail, see the reference files inside the skill folder:

- [references/api-contract.md](references/api-contract.md) - verified MCP tool names and schemas.
- [references/model-selection.md](references/model-selection.md) - decision matrix with worked examples.
- [references/credit-costs.md](references/credit-costs.md) - per-model credit costs.
- [references/marketing-studio-presets.md](references/marketing-studio-presets.md) - canned modes.
- [references/prompting-cookbook.md](references/prompting-cookbook.md) - per-model prompt templates.
- [references/soul-character-workflow.md](references/soul-character-workflow.md) - character training.
- [references/remotion-handoff.md](references/remotion-handoff.md) - video-config.yaml format.
- [references/troubleshooting.md](references/troubleshooting.md) - failure modes and fixes.

Issues and contributions: https://github.com/nuwansamaranayake/AiGNITEClaudeAssets/issues.
