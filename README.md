# AiGNITE Mobile Development Skills Suite

Eight Claude Code skills that turn a solo founder into a one-person mobile app studio. Each skill is a discipline. Together they take an idea from "what should this be" to "submitted to the App Store" without the operator writing a line of boilerplate.

Built by Nuwan Samaranayake at AiGNITE Consulting LLC. Used in production to ship one new mobile product every two weeks.

## What is in the suite

| Order | Skill | What it does |
|------:|-------|--------------|
| 1 | mobile-app-scaffold     | Generates a production-ready Expo project pre-wired for AiGNITE conventions in under sixty seconds. |
| 2 | mvp-design-framework    | Forces the five-question MVP discipline before any code gets written. |
| 3 | supabase-bootstrap      | Stands up Supabase with RLS on by default, verifies table count, generates the API contract. |
| 4 | security-audit          | Three-pass audit (identify, fix, regression check) before any submission. |
| 5 | design-from-mockup      | Takes a reference image or text prompt and produces a pixel-close mobile UI through a screenshot diff loop. |
| 6 | three-tier-test         | Chrome to mirror to physical device. Each tier must pass before the next runs. |
| 7 | app-store-submission    | Generates privacy policy, screenshots, metadata, reviewer credentials. Runs EAS submit. |
| 8 | mcp-to-mobile           | Flagship pipeline. Takes any AiGNITE MCP server URL and produces a full consumer mobile app with subscriptions and push notifications. |
| 9 | higgsfield-media        | Wraps the Higgsfield MCP server (Soul V2, Nano Banana Pro, Flux 2 Pro, Kling 3.0, Seedance 2.0, Veo 3.1, Sora 2 and more) into a disciplined image and video generation pipeline. Picks the right model per brief, tracks credit cost, hands off to remotion-video for assembly. |

## Who this is for

- Solo founders shipping mobile apps.
- AiGNITE Consulting operators wrapping MCP infrastructure into B2C products.
- Teams using Claude Code who need discipline without ceremony.

## How the skills compose

The skills depend on each other. A new project follows the order in the table. The `mcp-to-mobile` skill orchestrates the other seven into a single command.

See [docs/architecture.md](docs/architecture.md) for the dependency graph.

## Installation

### Option A: install everything

```powershell
.\INSTALL.ps1
```

The script copies every skill into `%USERPROFILE%\.claude\skills`. Existing skill folders are replaced.

### Option B: install one skill

```powershell
Copy-Item -Recurse "skill-name" -Destination "$env:USERPROFILE\.claude\skills\skill-name" -Force
```

### Option C: update

```powershell
.\UPDATE.ps1
```

Pulls the latest from this repo and re-installs.

## Engineering standards

These are non-negotiable. Every skill enforces them.

1. Root-cause fixes only. Curl the failing endpoint, query the database, read the logs before any fix.
2. Smoke tests verify real business endpoints, not health checks.
3. No silent mock data fallbacks outside development.
4. Verify table count after every database migration.
5. Maintain an API contract document.

See [docs/skill-development.md](docs/skill-development.md) for the full writing style guide and the standards reproduced in each skill.

## Writing style

The skills produce output users read. Every user-facing string follows these rules:

- Clear simple language. Short sentences. Active voice.
- No em dashes. No semicolons in prose.
- No metaphors or cliches.

The full avoid list and rationale are in `docs/skill-development.md`.

## Status

Version 0.2.1. Built 2026-05-12. Higgsfield MCP smoke-tested live.

## License

See [LICENSE](LICENSE).

## Contributing

Adding a ninth skill? See [docs/skill-development.md](docs/skill-development.md) for the standards.

## Acknowledgements

Built by Claude Code (Anthropic) under direction from Nuwan Samaranayake. The discipline of each skill reflects lessons paid for in real AiGNITE post-mortems, listed in the references within each skill.
