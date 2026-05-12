# Changelog

All notable changes to the AiGNITE Mobile Development Skills Suite go here.

The format follows Keep a Changelog. Versioning follows Semantic Versioning.

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
