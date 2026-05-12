# Changelog

All notable changes to the AiGNITE Mobile Development Skills Suite go here.

The format follows Keep a Changelog. Versioning follows Semantic Versioning.

## [0.2.1] - 2026-05-12

Smoke test passed. Live API contract verified and documented.

### Added

- `higgsfield-media/references/api-contract.md`. Records the verified tool names, parameter shapes, model IDs, and response schemas from the live MCP at `https://mcp.higgsfield.ai/mcp`. Last verified 2026-05-12.
- Linked the new reference from the skill's References section.

### Verified

- 17 tools live on the hosted MCP. Tool names differ from the original spec in several places (e.g. `balance` not `get_credit_balance`, `show_characters` not `list_characters`). The skill is anchored on the verified names.
- `generate_image` accepts `params.get_cost: true` for inline cost preflight, removing the need for a separate balance-tool call before generating.
- End-to-end pipeline: OAuth, workspace selection, model recommendation, cost preflight, generation (Flux 2 Pro, 1 credit), download, PNG validation, manifest write, credit ledger append. All green.

## [0.2.0] - 2026-05-12

Added `higgsfield-media` skill.

### Added

- `higgsfield-media` skill. Wraps the Higgsfield MCP server into a brief-driven image and video pipeline. Picks the right model (Soul V2, Nano Banana Pro, Flux 2 Pro, GPT Image 2, Seedream 4.5, Seedream 5.0 Lite, Kling O1 Image, Kling 3.0, Seedance 2.0, Wan 2.6, Hailuo 02, Veo 3.1, Sora 2). Confirms credit cost before generating. Tracks every generation in a per-project `manifest.json` and a global `credit-ledger.csv`. Hands off to `remotion-video` for clip assembly.
- Seven reference files (model-selection, credit-costs, marketing-studio-presets, prompting-cookbook, soul-character-workflow, remotion-handoff, troubleshooting).
- Seven prompt templates (LinkedIn cover, product hero, blog hero, 5-second ad clip, 15-second cinematic, UGC talking head, architecture backdrop).
- Three asset templates (manifest.json, credit-ledger.csv, video-config-from-higgsfield.yaml).
- Five scripts (check-mcp, check-balance, smoke-test, poll-job, batch-generate).
- Repo-level README, CHANGELOG, INSTALL.ps1, and `docs/architecture.md` updated to include the ninth skill.

### Engineering standards extension

Standard 6 added for this skill: confirm with the user before any single generation over 40 credits or any batch over 100 credits. Maintain a project manifest and a global credit ledger.

## [0.1.0] - 2026-05-12

Initial release.

### Added

- `mobile-app-scaffold` skill. Generates an Expo project with AiGNITE conventions.
- `mvp-design-framework` skill. Forces the five-question MVP discipline.
- `supabase-bootstrap` skill. Stands up Supabase with RLS and verified table count.
- `security-audit` skill. Three-pass identify / fix / regression audit.
- `design-from-mockup` skill. Asset extraction and screenshot diff loop.
- `three-tier-test` skill. Chrome to mirror to physical device test sequence.
- `app-store-submission` skill. EAS Submit pipeline with privacy policy publish.
- `mcp-to-mobile` skill. Flagship orchestrator that wraps any AiGNITE MCP into a mobile app.
- Repo-level installer (`INSTALL.ps1`) and updater (`UPDATE.ps1`).
- Engineering standards document baked into every project the skills generate.
- AiGNITE writing style guide enforced across user-facing output.

### Engineering standards (frozen at v0.1.0)

1. Root-cause fixes only.
2. Smoke tests verify real business endpoints, not health checks.
3. No silent mock data fallbacks outside development.
4. Verify table count after every database migration.
5. Maintain an API contract document.
