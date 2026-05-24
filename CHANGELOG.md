# Changelog

All notable changes to the AiGNITE Claude Skills go here.

The format follows Keep a Changelog. Versioning follows Semantic Versioning.

## [0.4.0] - 2026-05-24

First skill in the new VPS Operations category. Built from a real install on a Hostinger KVM 4 box; every surprise captured in the lessons file.

### Added

- `hermes-vps-deploy` skill. Stands up [Hermes Agent](https://hermes-agent.nousresearch.com) (Nous Research) on any Linux VPS that already runs Docker plus Traefik. Discovers the existing Traefik network and cert resolver via `docker inspect` rather than hardcoding. Generates a 32-char random Traefik basic-auth password, bcrypts it, and bakes the hash into a Traefik label with correct `$$` compose escaping. Brings up ONE container running `hermes gateway run` with `HERMES_DASHBOARD=1` so the dashboard runs as a side-process in the same PID namespace (per the official Hermes docs; splitting into two containers BREAKS the dashboard liveness probe). Runs strict smoke tests with no `-k` curl flag: external DNS, TLS chain verification with depth check, 401 challenge from Traefik, 200 from the dashboard with creds, cert subject and dates.
- `hermes-vps-deploy/assets/install.sh` unattended end-to-end installer for non-Claude operators. Reads inputs from environment variables (`SSH_ALIAS`, `HERMES_SUBDOMAIN`, `TRAEFIK_BASIC_AUTH_USER`, `CONTAINER_CPU_LIMIT`, `CONTAINER_MEMORY_LIMIT`). Idempotent: skips already-done steps on re-run.
- `hermes-vps-deploy/assets/docker-compose.template.yml` with placeholders for the network, cert resolver, subdomain, htpasswd hash, and resource limits.
- `hermes-vps-deploy/references/lessons.md` documenting 14 numbered lessons paid for in the reference deploy. Topics: one-container design, no native dashboard password, gateway subcommand is for messaging not HTTP, default model goes in config.yaml not .env, skill-sync prelude needs `start_period >= 60s`, the in-image compose file is dashboard-only, compose `$$` doubling for bcrypt hashes (with the `docker compose config` display artifact gotcha), `docker exec -u hermes` requirement for state-writing subcommands, Traefik discover-don't-assume pattern, exact env var names that are correct as-is, failure modes the strict smoke tests catch, Hostinger snapshot via MCP API, and things prepared for that didn't happen.
- `hermes-vps-deploy/references/follow-on-extensions.md` covering Anthropic OAuth via Claude subscription (dashboard + CLI flows), Telegram pairing (with the `docker exec -u hermes` fix for the pairing-file ownership bug), MCP server wiring including the undocumented `transport: sse` workaround for SSE-only MCPs, and Gmail monitoring via the bundled himalaya CLI on a `--no-agent` cron in silent-when-empty mode.
- New top-level category in the README: "VPS Operations". The architecture in `docs/architecture.md` already anticipated horizontal categories so no restructuring needed.
- `INSTALL.ps1` updated to install the new skill. Synopsis revised from "eight Mobile Development Skills" to "all AiGNITE Claude Skills" to match the broader scope.

### Engineering standards extension

Standard 7 added for VPS deploys: every deploy that touches Traefik or DNS must include a strict smoke test phase that verifies TLS chain depth `>=2` and `Verification: OK` without `-k`. This catches the leaf-only cert chain failure mode that `curl -k` masks.

### Migration notes

No breaking changes. Existing skills, frontmatter, and APIs are unchanged. The new skill is additive and does not interact with the Mobile Development pipeline.

## [0.3.0] - 2026-05-12

Rebrand and restructure. The collection is now generic enough to host multiple skill families, not only mobile development.

### Changed

- Suite renamed from "AiGNITE Mobile Development Skills Suite" to "AiGNITE Claude Skills" across every README, doc, and skill reference.
- Top-level `README.md` reorganized around categories. Current categories: Mobile Development (8 skills) and Media Generation (1 skill). Future categories slot in without restructuring.
- `docs/architecture.md` updated to describe Mobile Development as one category among several, with horizontal skills like `higgsfield-media` slotting in across categories.

### Added

- `higgsfield-media/USERGUIDE.md`. Comprehensive end-to-end walkthrough: prerequisites, install, OAuth, first generation, common workflows (LinkedIn cover, product hero, blog hero, motion clips, cinematic ads, UGC, architecture backdrops), multiple-variant batches, Soul Character training, Remotion handoff, credit budget management, output organization, troubleshooting, and tips.

### Migration notes

No breaking changes. Skill names, frontmatter, file paths, and APIs are unchanged. The rebrand is documentation-only.

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
