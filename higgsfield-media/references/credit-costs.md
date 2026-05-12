# Credit Costs

One-line summary: Current Higgsfield credit prices per model on the Plus plan, with last-verified date and the source URL. Prices drift; verify before budgeting a large batch.

## Last verified

Date: 2026-05-12
Source: https://higgsfield.ai/pricing (Plus plan, annual billing)
Plan: Higgsfield Plus, $39 per month annual, 1,000 monthly credits, 6 parallel video jobs, 8 parallel image jobs.

## Unlimited tier on Plus

These cost zero credits on the Plus plan. Use freely.

| Model | Resolution cap on Plus |
|-------|------------------------|
| Flux 2 Pro | Up to 4K |
| Seedream 4.5 | 1080p on Plus, 4K on Ultra |
| Seedream 5.0 Lite | 1080p |
| GPT Image 2 | 4K |
| Kling O1 Image | 1080p |
| Nano Banana 2 | 2K |

## Free pool tier

5,000 generations per month included in Plus across these models. Counts as free until the pool is exhausted.

| Model |
|-------|
| Soul V2 |
| Cinema Studio |
| Soul Cinema |

## Light paid tier (image)

| Model | Credits per image | Notes |
|-------|-------------------|-------|
| Nano Banana Pro | ~2 | 4K text rendering, packaging |

## Mid paid tier (video)

| Model | Credits per 5-sec clip | Notes |
|-------|------------------------|-------|
| Wan 2.6 | ~5 | Budget tier, fast iteration |
| Kling 2.5 Turbo | ~3 | Preview, prompt validation |
| Kling 2.6 | ~5 | Mid-tier production |
| Kling 3.0 | ~6 | House default, 4K, camera control |
| Hailuo 02 | ~5 | Character animation |

## Heavy paid tier (video)

| Model | Credits per 5-sec clip | Notes |
|-------|------------------------|-------|
| Seedance 2.0 | ~9 | Audio-video sync, single pass |

## Premium tier (video)

| Model | Credits per clip | Notes |
|-------|------------------|-------|
| Veo 3.1 | 40 to 70 | 8-second narrative, save for finals |
| Sora 2 | 40 to 70 | 15-second cinematic, physics |

## Daily budget rules of thumb

- 1,000 credits per month means about 33 credits per day average.
- One Veo 3.1 or Sora 2 generation can burn two days of average budget. Plan accordingly.
- A typical image batch of 10 with Nano Banana Pro is 20 credits.
- A typical Kling 3.0 social cut at 4K is 6 credits.

## Confirmation thresholds

The skill confirms with the user before:

- Any single generation over 40 credits
- Any batch totaling over 100 credits

These thresholds are encoded in Phase 4 of `SKILL.md`.

## When credit prices change

Higgsfield revises pricing periodically. If the skill encounters a credit cost in the API response that differs from this file by more than 20 percent, log the new price and prompt the user to re-verify before proceeding.

## Plus plan limits

- 1,000 credits per month, no rollover
- 6 parallel video jobs maximum
- 8 parallel image jobs maximum
- 365-day unlimited access on the unlimited tier
- 5,000 free Soul V2 plus Cinema generations per month
- 2K unlimited on Nano Banana 2
- Lipsync Studio included

When a batch exceeds the parallel cap, chunk the jobs. The skill chunks image jobs in groups of 8 and video jobs in groups of 6 automatically.
