# AiGNITE Claude Skills

A collection of production-grade Claude Code skills. Each one encodes a discipline that turns a creative brief, a vague idea, or a routine task into reliable, shippable work without the operator writing boilerplate.

Built and maintained by Nuwan Samaranayake at AiGNITE Consulting LLC. Used in production. Open-sourced under MIT for anyone running Claude Code.

## Why use these skills

Claude Code is powerful out of the box. These skills add three things on top:

1. **Discipline.** Every skill enforces hard rules. No silent fallbacks. No mock data in production. Verify before assuming.
2. **Composition.** Skills hand off to each other through file artifacts (`MVP_SPEC.md`, `API_CONTRACT.md`, `manifest.json`). You can swap one without breaking the others.
3. **Real prompts.** Each skill ships with at least three substantive trigger phrases that match how operators actually talk.

## Skill catalog

### Mobile Development

Eight skills that take a mobile app from idea to App Store submission. Designed for solo founders shipping consumer apps on Expo plus Supabase. Compose into the `mcp-to-mobile` flagship pipeline.

| Skill | What it does |
|-------|--------------|
| [mvp-design-framework](mvp-design-framework/) | Forces five-question MVP discipline before any code gets written. |
| [mobile-app-scaffold](mobile-app-scaffold/) | Generates a production-ready Expo project pre-wired for AiGNITE conventions in under sixty seconds. |
| [supabase-bootstrap](supabase-bootstrap/) | Stands up Supabase with RLS on by default, verifies table count, generates the API contract. |
| [design-from-mockup](design-from-mockup/) | Takes a reference image or text prompt and produces a pixel-close mobile UI through a screenshot diff loop. |
| [security-audit](security-audit/) | Three-pass audit (identify, fix, regression check) before any submission. |
| [three-tier-test](three-tier-test/) | Chrome to mirror to physical device. Each tier must pass before the next runs. |
| [app-store-submission](app-store-submission/) | Generates privacy policy, screenshots, metadata, reviewer credentials. Runs EAS submit. |
| [mcp-to-mobile](mcp-to-mobile/) | Flagship pipeline. Takes any MCP server URL and produces a full consumer mobile app with subscriptions and push notifications. |

See [docs/architecture.md](docs/architecture.md) for the dependency graph and build order.

### Media Generation

| Skill | What it does |
|-------|--------------|
| [higgsfield-media](higgsfield-media/) | Wraps the Higgsfield MCP server (30 plus models including Soul V2, Nano Banana Pro, Flux 2 Pro, Kling 3.0, Seedance 2.0, Veo 3.1, Sora 2). Brief in plain language, get the right model picked, credit cost confirmed, asset downloaded, manifest written. [User's guide here.](higgsfield-media/USERGUIDE.md) |

### More categories coming

The suite is structured to host future skill families. Engineering ops, content generation, research workflows, finance, devops all fit the same pattern: pushy description, hard rules, file-based handoff, MIT license.

## Installation

### Install everything at once

```powershell
git clone https://github.com/nuwansamaranayake/AiGNITEClaudeAssets.git
cd AiGNITEClaudeAssets
.\INSTALL.ps1
```

The script copies every skill into `%USERPROFILE%\.claude\skills`. Existing folders are replaced.

### Install a single skill

```powershell
git clone https://github.com/nuwansamaranayake/AiGNITEClaudeAssets.git
cd AiGNITEClaudeAssets
Copy-Item -Recurse "skill-name" -Destination "$env:USERPROFILE\.claude\skills\skill-name" -Force
```

### Update later

```powershell
.\UPDATE.ps1
```

Pulls latest from `main` and re-installs.

## Engineering standards

Every skill enforces these. Non-negotiable.

1. Root-cause fixes only. Curl the failing endpoint, query the database, read the logs before any fix.
2. Smoke tests verify real business endpoints, not health checks.
3. No silent mock data fallbacks outside development.
4. Verify table count after every database migration.
5. Maintain an API contract document.
6. Confirm with the user before any cost commitment over the configured threshold.

See [docs/skill-development.md](docs/skill-development.md) for the full writing style guide and the standards reproduced in each skill.

## Writing style

The skills produce output users read. Every user-facing string follows:

- Clear simple language. Short sentences. Active voice.
- No em dashes. No semicolons in prose.
- No metaphors or cliches.

Full avoid list in `docs/skill-development.md`.

## Status

Version 0.3.0. Built 2026-05-12. Higgsfield MCP smoke-tested live.

## License

MIT. See [LICENSE](LICENSE).

## Contributing

Adding a tenth skill (or a new category)? See [docs/skill-development.md](docs/skill-development.md). PRs welcome.

## Acknowledgements

Built by Claude Code (Anthropic) under direction from Nuwan Samaranayake. The discipline of each skill reflects lessons paid for in real post-mortems, listed in the references within each skill.
