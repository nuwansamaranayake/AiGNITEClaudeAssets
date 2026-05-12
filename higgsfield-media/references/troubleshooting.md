# Troubleshooting

One-line summary: The most common Higgsfield MCP failure modes and the fix for each.

## OAuth token expired

Symptom: every tool call returns 401 or "authentication required".

Fix: re-run the OAuth flow.

1. Open the Claude Code `/mcp` panel.
2. Find higgsfield in the list.
3. Click reauthenticate. A browser opens.
4. Complete the OAuth flow.
5. Return to the session. Retry the failing tool call.

Do not script the OAuth refresh. The flow is browser-based by design.

## Video job stuck past 5 minutes

Symptom: `get_generation_status` keeps returning `processing` past the 5-minute polling cap.

Fix:

1. Surface the job handle to the user.
2. Stop polling.
3. Print a message: "Your job is still processing. Check status manually with `get_generation_status` and the job handle below."
4. Save the job handle to the manifest under `pending_jobs`.

The user can resume later by passing the handle back. Do not silently keep polling and burn user attention.

## Model not found

Symptom: tool returns "model not found" with a typo in the slug.

Fix:

1. Run `claude mcp get higgsfield` in a scratch directory.
2. Read the live tool list and the documented model slugs.
3. Update `assets/templates/*` and `references/credit-costs.md` with the corrected slug.
4. Retry the generation.

Note: model slugs change when Higgsfield ships new versions. Anchor on the official hosted server at `https://mcp.higgsfield.ai/mcp`.

## Parallel job cap exceeded

Symptom: the seventh video job (or ninth image job) returns "rate limit" or "parallel cap exceeded" on Plus.

Fix:

1. Chunk the batch.
2. Image jobs in groups of 8 maximum.
3. Video jobs in groups of 6 maximum.
4. Submit one chunk, wait for half the chunk to complete, submit the next.

The `scripts/batch-generate.py` script handles this automatically.

## Credit exhaustion mid-batch

Symptom: a batch starts at 60 credits remaining, generates 50 credits of jobs, then the next job fails with "insufficient credits".

Fix:

1. The preflight is supposed to catch this. If it leaked past, halt the batch.
2. Write a partial manifest with `status: aborted-low-balance`.
3. Print a one-line summary of what was generated and what was skipped.
4. Suggest the user upgrade the plan or wait until the next monthly cycle.

## Schema drift

Symptom: tool returns an error that does not match the documented schema, or fields appear in responses that the skill does not handle.

Fix:

1. Log the unexpected response to `output/schema-drift.log`.
2. Continue the generation if the core fields (url, credits, job_id) are present.
3. Surface a non-blocking warning to the user.
4. Open an issue against the skill so the maintainer updates the schema.

Schema drift is expected on a fast-moving MCP. The skill survives it by reading core fields permissively.

## OAuth flow opens the wrong browser

Symptom: the reauthentication flow opens in a browser that is not logged into Higgsfield, or in a Private window.

Fix:

1. Copy the URL from the browser address bar.
2. Open the same URL in your default browser logged into Higgsfield.
3. Complete the flow there.
4. Return to Claude Code and retry.

## Generation returns a low-quality result

Symptom: the output looks worse than expected.

Fix:

1. Check the prompt against the cookbook for the chosen model.
2. Verify the resolution parameter matches the plan tier (Plus is 1080p on some models, 4K on others).
3. Regenerate with a tightened prompt.
4. If the issue persists, switch to the fallback model in the decision matrix.

## The skill triggers on the wrong brief

Symptom: the skill fires on "find me a stock image" when the user wanted image search, not generation.

Fix:

1. Acknowledge the intent mismatch.
2. Suggest the appropriate alternative (web search, an image-lookup tool).
3. Do not generate a paid image when the user wanted a free stock photo.

The skill description excludes plain "image" or "video" without a generation verb. Verify the user's intent before generating.

## Manifest file corrupted by partial write

Symptom: `manifest.json` is invalid JSON because a crash mid-write left a partial entry.

Fix:

1. The skill writes manifest entries one generation at a time using an atomic temp-file write.
2. If corruption still happens, the skill keeps a `.manifest.json.backup` file copied before every write.
3. On startup, validate the manifest. If invalid, restore from `.backup`.
4. Re-record the last generation by reading the credit ledger.

The backup mechanism is automatic and lives in `scripts/batch-generate.py`.
