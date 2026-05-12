# API Contract

One-line summary: The verified Higgsfield MCP tool names and parameter shapes as of the smoke-test date. Anchor on this when the live MCP drifts.

## Verification

Last verified: 2026-05-12 against the hosted server at `https://mcp.higgsfield.ai/mcp`. Smoke test ran end-to-end (generate plus download plus file validation) on this date.

When the live MCP returns shapes that differ from this file by more than a field name, log the drift in `output/schema-drift.log` and update this file with the corrected shape.

## Tool inventory (17 tools)

| Tool name | Purpose | Auth required |
|-----------|---------|----------------|
| `mcp__higgsfield__authenticate` | Start the OAuth flow, returns the authorize URL | No |
| `mcp__higgsfield__complete_authentication` | Complete OAuth if the redirect listener missed it | No |
| `mcp__higgsfield__balance` | Return `{credits, subscription_plan_type}` | Yes |
| `mcp__higgsfield__show_plans_and_credits` | Detailed plan view | Yes |
| `mcp__higgsfield__list_workspaces` | List user workspaces with `is_selected` flag | Yes |
| `mcp__higgsfield__select_workspace` | Set or clear the active workspace | Yes |
| `mcp__higgsfield__models_explore` | List, search, get, or recommend models | Yes |
| `mcp__higgsfield__generate_image` | Submit an image generation job | Yes |
| `mcp__higgsfield__generate_video` | Submit a video generation job | Yes |
| `mcp__higgsfield__job_status` | Poll a job by ID | Yes |
| `mcp__higgsfield__job_display` | Show one or more completed jobs in the widget | Yes |
| `mcp__higgsfield__show_generations` | Browse generation history | Yes |
| `mcp__higgsfield__show_characters` | List or train Soul Characters | Yes |
| `mcp__higgsfield__show_marketing_studio` | Browse Marketing Studio presets | Yes |
| `mcp__higgsfield__show_medias` | List uploaded reference media | Yes |
| `mcp__higgsfield__media_upload` | Upload a local file as a reference asset | Yes |
| `mcp__higgsfield__media_confirm` | Confirm media upload after URL pre-signing | Yes |
| `mcp__higgsfield__transactions` | Credit transaction history | Yes |
| `mcp__higgsfield__virality_predictor` | Predict video virality and engagement | Yes |

Note on the original spec: the spec assumed tool names like `get_credit_balance`, `list_characters`, `create_character`, `get_generation_status`. The live server uses the names above. The skill text references the verified names.

## generate_image contract

```json
{
  "params": {
    "model": "<model_id from models_explore>",
    "prompt": "<text prompt>",
    "aspect_ratio": "1:1 | 4:3 | 3:4 | 16:9 | 9:16 | 3:2 | 2:3 | 21:9 | 9:21",
    "count": 1,
    "get_cost": false,
    "medias": [
      { "value": "<uuid_or_url>", "role": "image" }
    ],
    "<model_specific_param>": "<value>"
  }
}
```

Cost preflight: set `params.get_cost: true` to receive `{ cost: { credits, credits_exact } }` without submitting a job. Not supported for Marketing Studio models.

Asynchronous: image jobs return a job ID in `results[].id`. Poll with `job_status`. Typical completion: 10 to 20 seconds.

Model variant parameters live inside `params`. Example for Flux 2: `params.model: "pro" | "flex" | "max"` and `params.resolution: "1k" | "2k"`.

## Verified model IDs (from models_explore)

| Human name in the skill | API model_id | Variants |
|-------------------------|--------------|----------|
| Flux 2 Pro | `flux_2` | `model: pro` (default), `flex`, `max`; `resolution: 1k`, `2k` |
| Flux Kontext Max | `flux_kontext` | (none surfaced in initial query) |
| Soul Cast (one-off character) | `soul_cast` | `budget` numeric param |
| Soul Location | `soul_location` | (none surfaced) |
| Z Image | `z_image` | (fast, stylized text-to-image) |

The original spec used slugs like `nano-banana-pro`, `kling-3-0`, `seedance-2-0`. Resolve the live ID for each of these by calling `models_explore` with `action: search` and the human name before generating. The skill does this automatically as part of Phase 3.

Filename convention in `output/<date>/<project>/`: kebab-case the human name (e.g. `001_flux-2-pro_1k_1c.png`). The API ID and the filename slug are intentionally different. The filename is for humans; the API call uses the verified ID.

## job_status contract

```json
{
  "jobId": "<uuid>",
  "sync": true,
  "raw_data": false
}
```

With `sync: true` the server polls internally for up to 25 seconds and returns on terminal state. Use this for image jobs (typical 10-20s). For video jobs (60-180s) use `sync: false` and poll every 8 seconds, surfacing the handle after 5 minutes per the skill's hard rule.

Response on completion:

```json
{
  "generation": {
    "id": "<uuid>",
    "type": "image | video",
    "status": "pending | processing | completed | failed",
    "model": "<model_id>",
    "params": { ... },
    "results": {
      "rawUrl": "<cdn url, lossless>",
      "minUrl": "<cdn url, optimized>"
    },
    "createdAt": <unix_seconds>
  }
}
```

## balance contract

```json
{
  "credits": 1010,
  "subscription_plan_type": "plus"
}
```

Plus plan refresh cadence: monthly, no rollover.

## list_workspaces contract

```json
{
  "workspaces": [
    {
      "id": "<uuid>",
      "name": null,
      "type": "private | team",
      "user_role": "owner | member",
      "is_selected": false,
      "plan_type": "plus | ultra | free",
      "credits": 1010
    }
  ]
}
```

Always call `select_workspace` if `is_selected: false`, otherwise generations target the wrong context.

## models_explore contract

Actions: `list`, `search`, `get`, `recommend`.

`recommend` ranks by goal plus input context. Returns up to 5 by default. Note that `recommend` queries can return negative-score items when no model fits perfectly; in those cases, fall through to `search` with a model name to confirm the slug.

`get` requires `model_id` and returns full parameter shape plus aspect ratio options.

## Failure modes observed during testing

1. `recommend` returned `z_image`, `soul_cast`, `soul_location` for an "abstract image" query with negative scores. The actual Flux 2 model was not in the top 5. Fall back to `search` with `query: "flux"`.

2. `get_cost` preflight defaults model variants when not specified. The response's `adjustments` field documents every defaulted parameter. The skill should echo these defaults to the user before generating.

3. CDN URLs are presigned and time-limited (typically 7 days). Download to local disk immediately after generation; do not rely on the URL persisting.

## When to update this file

Update on any of:

- A tool name change (e.g. `generate_image` is renamed)
- A new tool added that the skill should use
- A parameter shape change
- A new model variant or model_id

Bump the "Last verified" date when running the smoke test or any production batch confirms current behavior.
