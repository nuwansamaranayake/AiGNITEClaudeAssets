# Skill Development Guide

One-line summary: How to add a ninth skill to the AiGNITE Claude Skills without breaking the discipline of the first eight.

## Anatomy of a skill

Every skill in the suite follows the same folder shape:

```
skill-name/
├── SKILL.md              # Required. YAML frontmatter plus markdown body.
├── README.md             # Brief overview for the repo browser.
├── references/           # On-demand docs Claude loads when needed.
│   └── *.md
├── scripts/              # Executable helpers (PowerShell or Python).
│   └── *.ps1
├── assets/               # Templates and configs the skill writes out.
│   ├── templates/
│   └── prompts/
└── evals/                # Test cases.
    └── evals.json
```

## SKILL.md frontmatter

The frontmatter is the only thing Claude sees in the skill metadata. Pack it. The description must be pushy because Claude under-triggers skills by default.

```yaml
---
name: skill-name-in-kebab-case
description: One sentence on what the skill does, then specific trigger contexts. Use the skill whenever the user mentions [keywords], even if they do not name the skill explicitly.
---
```

Rules for the description:

- Lead with what the skill does.
- List five to eight trigger phrases verbatim from how a real user would talk.
- End with the explicit "even if they do not name the skill" line.
- Total length 250 to 500 characters.

## SKILL.md body

Markdown. Sections in this order:

1. Purpose (one paragraph)
2. When to trigger (bullet list)
3. Inputs to collect
4. Behavior (numbered steps)
5. Hard constraints
6. Refusals
7. Composes with
8. References

Keep the body under 500 lines. Push deep content into `references/` and link to it.

## Writing style

The skills produce text users read. Follow these rules in any user-facing output your skill prints. Apply the same rules to SKILL.md bodies for consistency.

- Clear simple language. Short sentences. Active voice.
- No em dashes. No semicolons in prose.
- No metaphors or cliches.
- No markdown asterisks for emphasis inside running prose.

### Avoid this list

Words and phrases banned across the suite:

- can, may, just, that, very, really, literally, actually, certainly, probably, basically, could, maybe
- delve, embark, enlightening, esteemed
- shed light, craft, crafting, imagine, realm
- game-changer, unlock, discover, skyrocket, revolutionize, disruptive
- utilize, utilizing, dive deep
- tapestry, illuminate, unveil, pivotal, intricate, elucidate
- hence, furthermore, however
- harness, exciting, groundbreaking, cutting-edge, remarkable, powerful, ever-evolving

The reasoning: these words signal AI-generated prose. AiGNITE output should sound like a senior engineer wrote it.

## Description must be pushy

Claude under-triggers skills with passive descriptions. Compare:

Weak:
> Helps with mobile app projects.

Strong:
> Generates a production-ready Expo React Native project pre-wired for AiGNITE conventions in under sixty seconds. Use this skill whenever the user mentions building a mobile app, scaffolding an Expo project, starting a new React Native app, mobile boilerplate, Expo scaffold, or kicking off a mobile project, even if they do not name the skill explicitly.

The strong version triggers on six different phrasings. The weak version triggers on none.

## Hard constraints belong in the skill, not in CLAUDE.md

Every skill in the suite has a "Hard constraints" section. These are the rules the skill refuses to violate. Examples:

- mobile-app-scaffold: never proceeds with an invalid bundle ID.
- supabase-bootstrap: never skips table count verification.
- security-audit: never marks an audit complete with open Critical findings.
- mcp-to-mobile: never exposes a tool not on the public-safe whitelist.

A new skill should name the constraints upfront and refuse rather than warn.

## Scripts

PowerShell for Windows-native operations. Python for cross-platform. Every script:

1. Accepts `-WhatIf` or `-DryRun` for preview.
2. Exits non-zero on failure.
3. Prints WROTE, RUN, or DRY prefixes for every file or command.
4. Validates inputs before any side effect.

## Asset templates

Templates use `{{VARIABLE_NAME}}` placeholders. Scripts substitute values via simple string replacement.

Never embed user-specific data in a template. Templates are static. Scripts render them.

## Eval format

Three test prompts per skill, in `evals/evals.json`:

```json
{
  "skill_name": "mobile-app-scaffold",
  "evals": [
    {
      "id": 1,
      "prompt": "Scaffold a mobile app called FloodPulse Mobile with bundle ID com.aignite.floodpulse",
      "expected_output": "A complete Expo project tree at the specified path with all standard AiGNITE conventions in place",
      "files": []
    }
  ]
}
```

Each prompt must be substantive enough to trigger a skill. Single-word prompts do not trigger.

## Composing with other skills

The skills communicate through file artifacts, not direct calls. If your new skill needs context from another skill, read the artifact:

- Need the MVP definition? Read `MVP_SPEC.md`.
- Need the database schema? Read `API_CONTRACT.md`.
- Need the security verdict? Read `SECURITY_AUDIT.md`.
- Need the test status? Read `TEST_RESULTS.md`.

If your skill produces new context downstream skills need, write to a known path and document the file in your SKILL.md.

## Engineering standards reproduced

The five non-negotiable rules every AiGNITE mobile project enforces:

1. Root-cause fixes only.
2. Smoke tests verify real business endpoints, not health checks.
3. No silent mock data fallbacks outside development.
4. Verify table count after every database migration.
5. Maintain an API contract document.

A new skill must respect every rule. Skills that work around a rule do not ship.

## Submitting a new skill

1. Create the folder structure.
2. Write SKILL.md following the shape above.
3. Write references, assets, scripts, and evals.
4. Add the skill to `INSTALL.ps1`.
5. Update the table in `README.md`.
6. Add a CHANGELOG entry.
7. Run the three evals against a fresh Claude Code session.
8. Open a PR.

The maintainer (Nuwan Samaranayake) reviews against this guide.
