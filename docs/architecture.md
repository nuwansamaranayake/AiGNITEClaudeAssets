# Architecture

One-line summary: How the eight AiGNITE Mobile Development Skills compose, the dependency graph, and the reasoning behind the build order.

## Dependency graph

```
mvp-design-framework
        |
        v
mobile-app-scaffold ─────┐
        |                |
        v                |
supabase-bootstrap       |
        |                |
        v                |
design-from-mockup       |
        |                |
        v                |
security-audit           |
        |                |
        v                |
three-tier-test          |
        |                |
        v                |
app-store-submission <───┘
                         |
                         |
                         |
mcp-to-mobile ───────────┘  (orchestrator that calls every other skill)
```

## Why this build order

### 1. mvp-design-framework first

Building before defining the MVP is the most common failure mode for solo founders. The framework runs in ten minutes. Skipping it costs weeks.

### 2. mobile-app-scaffold second

The scaffold encodes every other skill's assumptions. The Supabase client expects keys at a specific path. The smoke test expects a specific structure. The audit expects a specific folder layout. Generate the scaffold once and everything downstream works.

### 3. supabase-bootstrap third

The database backs everything. The migration runs against the project structure the scaffold produced. The API contract feeds the security audit, the three-tier test, and the submission metadata.

### 4. design-from-mockup fourth (optional)

This is the only optional skill. A scaffold with default styling is acceptable for utility apps. For consumer apps, the mockup pipeline is the difference between "looks like a developer made it" and "looks like a real product".

### 5. security-audit fifth

Audit before testing. A vulnerability discovered after the three-tier test means rebuilding the dev artifacts and re-running everything. Audit first so the test artifacts are stable.

### 6. three-tier-test sixth

Test after audit so fixes do not bypass the test suite. The three tiers (Chrome, mirror, physical device) catch what the previous tier misses.

### 7. app-store-submission seventh

Submit after test and audit. The submission skill refuses to run without recent passes from both.

### 8. mcp-to-mobile eighth

The orchestrator depends on every other skill. It is built last because it composes the others.

## Communication between skills

Skills do not call each other directly. They communicate through artifacts the project produces:

- `MVP_SPEC.md` (written by mvp-design-framework, read by everyone)
- `CLAUDE.md` (written by mobile-app-scaffold, read by every Claude session in the project)
- `API_CONTRACT.md` (written by supabase-bootstrap, read by security-audit and three-tier-test)
- `SECURITY_AUDIT.md` (written by security-audit, read by app-store-submission)
- `TEST_RESULTS.md` (written by three-tier-test, read by app-store-submission)
- `scripts/smoke-test.sh` (written by mobile-app-scaffold, executed by three-tier-test)

This file-based protocol keeps the skills loosely coupled. A skill can be replaced without breaking the others as long as it produces the right artifacts.

## What every project ends up with

After running all eight skills, a project root contains:

```
my-app/
├── app/                       # Expo Router screens (one per MCP tool if mcp-to-mobile)
├── components/
├── lib/
├── hooks/
├── services/
├── assets/
├── scripts/
│   └── smoke-test.sh
├── supabase/
│   └── migrations/
├── store/
│   ├── privacy-policy.md
│   ├── support.md
│   ├── app-store-metadata.yaml
│   └── screenshots/
├── design/
│   ├── reference.png
│   ├── tokens.json
│   └── iterations.log
├── MVP_SPEC.md
├── API_CONTRACT.md
├── SECURITY_AUDIT.md
├── TEST_RESULTS.md
├── CLAUDE.md
├── README.md
├── Makefile
├── app.json
├── eas.json
├── package.json
├── tsconfig.json
├── eslint.config.js
├── prettier.config.js
├── .env.local.example
└── .gitignore
```

## Extension points

A ninth skill fits the suite if it:

1. Writes its outputs to a known file path.
2. Reads inputs from known file paths.
3. Composes with the engineering standards.
4. Refuses to run when upstream artifacts are missing or stale.

See [skill-development.md](skill-development.md) for the standards.
