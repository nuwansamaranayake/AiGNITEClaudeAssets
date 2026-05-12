# Claude Code Build Prompt: AiGNITE Mobile Development Skills Suite

## Mission

You are building a production-grade Claude Code skills suite for AiGNITE Consulting. Create eight skills in `E:\AiGNITE\projects\custom-skills` that together turn the founder, Nuwan Samaranayake, into a one-person mobile app studio. After building each skill, install it into the user-level Claude environment so it loads automatically across all future Claude Code sessions.

These skills will also be packaged for sale as a training repo. Build them to that standard.

## Context You Must Hold

Read this carefully. Every skill you build must reflect these realities.

**The operator.** Nuwan runs AiGNITE Consulting LLC in Houston and AiGNITE Software Pvt Ltd in Sri Lanka. He ships one new product every two weeks using a three-tier pattern: Data Ingestion, Intelligence Engine, MCP Server. He has six live MCP servers in production: Beacon GoM, RegScope, RecallWatch AI, FloodPulse, AirShield, and Cosmic Nexus. The mobile skills you build must compose with this MCP infrastructure.

**The infrastructure.** Hostinger VPS in Houston for US products, Hostinger VPS in Mumbai for Sri Lankan products. Traefik reverse proxy, Docker Compose, PostgreSQL with pgvector. Central YAML port registry prevents port collisions across 11 products. Resend for transactional email via contact.aigniteconsulting.ai. Stripe for billing.

**The engineering standards.** Non-negotiable. Every skill must enforce them.

1. Root-cause fixes only. Before any bug fix, curl the failing endpoints, query the database, read the logs, document what is actually broken versus what is reported. Never patch frontend display issues when the backend is broken.
2. Smoke tests verify real business endpoints, not health checks. Curl every API with a real token. Verify non-empty responses. Confirm database tables exist with expected row counts.
3. No silent mock data fallbacks in non-development environments. If an API fails, show an error. Never show fake data that masks system failures.
4. Verify table count after every database migration. Partial migration failures are silent killers. GoviHub lost five days because ten tables silently failed to create and the frontend fell back to mock data.
5. Maintain an API contract document. List every URL the frontend calls, map it to the backend endpoint, verify they match before deployment.

**The writing style.** Inside every skill the user sees, follow this. Clear simple language. Short impactful sentences. Active voice. No em dashes ever. No semicolons. No metaphors or cliches. No hashtags. No markdown asterisks for emphasis inside running prose. Avoid these words specifically: can, may, just, that, very, really, literally, actually, certainly, probably, basically, could, maybe, delve, embark, enlightening, esteemed, shed light, craft, crafting, imagine, realm, game-changer, unlock, discover, skyrocket, revolutionize, disruptive, utilize, utilizing, dive deep, tapestry, illuminate, unveil, pivotal, intricate, elucidate, hence, furthermore, however, harness, exciting, groundbreaking, cutting-edge, remarkable, powerful, ever-evolving. Markdown inside SKILL.md files is fine because those are technical documents Claude reads, but user-facing output the skills generate must follow the style guide.

## Build Order

Build in this sequence. Each skill builds on the previous ones.

1. mobile-app-scaffold
2. mvp-design-framework
3. supabase-bootstrap
4. security-audit
5. design-from-mockup
6. three-tier-test
7. app-store-submission
8. mcp-to-mobile

## Pre-Flight Checks

Before writing any skill, run these checks.

```bash
# Verify target directory exists, create if missing
if (!(Test-Path "E:\AiGNITE\projects\custom-skills")) {
    New-Item -ItemType Directory -Path "E:\AiGNITE\projects\custom-skills" -Force
}

# Verify Claude Code user skills directory exists
$claudeSkillsDir = "$env:USERPROFILE\.claude\skills"
if (!(Test-Path $claudeSkillsDir)) {
    New-Item -ItemType Directory -Path $claudeSkillsDir -Force
}

# Verify Claude Code is installed and on PATH
claude --version
```

If any check fails, fix it before proceeding. Tell the user what you fixed.

## Standard Skill Anatomy

Every skill in this suite must follow this structure.

```
skill-name/
├── SKILL.md              # Required. YAML frontmatter plus markdown body.
├── README.md             # Brief overview for the repo, not loaded by Claude
├── references/           # Reference docs Claude loads when needed
│   └── *.md
├── scripts/              # Executable helpers
│   └── *.ps1 or *.py
├── assets/               # Templates, configs, schemas the skill writes out
│   └── *
└── evals/                # Test cases for skill verification
    └── evals.json
```

## SKILL.md Frontmatter Requirements

Every SKILL.md starts with this exact frontmatter shape. The description must be pushy because Claude under-triggers skills by default.

```yaml
---
name: skill-name-in-kebab-case
description: One sentence on what the skill does, then specific trigger contexts. Make sure to use this skill whenever the user mentions [specific keywords], even if they do not explicitly ask for the skill by name.
---
```

The description is the only thing Claude sees in metadata. Pack it. Include the keywords a real user would say. Repeat trigger phrases in different surface forms.

## Skill 1: mobile-app-scaffold

**Purpose.** Generate a production-ready Expo React Native project pre-wired for AiGNITE conventions in under sixty seconds.

**Triggers on.** "Build a mobile app", "scaffold an Expo project", "new React Native app", "start a mobile project", "Expo scaffold", "mobile app boilerplate".

**What it produces.**

- `app.json` and `eas.json` with placeholders for bundle ID, owner, version
- Folder layout: `app/` (Expo Router), `components/`, `lib/`, `hooks/`, `services/`, `assets/`
- `lib/supabase.ts` with client initialization and RLS-aware queries
- `services/mcp-client.ts` that points at any AiGNITE MCP server URL
- `.env.local.example` with every variable the project needs
- `CLAUDE.md` at project root with the AiGNITE engineering standards baked in
- `Makefile` with three targets: `make check`, `make up`, `make smoke`
- `scripts/smoke-test.sh` that curls every business endpoint with a real token and counts DB tables
- `.gitignore` correctly configured
- `tsconfig.json` with strict mode on
- `eslint.config.js` and `prettier.config.js` with no-em-dash rule custom-added

**Smoke test behavior.** The generated `make smoke` must call real business endpoints. No health-check-only smoke tests. If a developer adds a new endpoint, the smoke test must fail until they add a probe for it. Document this in the skill.

**Reference files to include.**

- `references/expo-conventions.md` - Expo Router structure, file naming, navigation patterns
- `references/aignite-coding-standards.md` - the engineering standards in full
- `references/folder-layout.md` - what goes where and why

**Asset files to include.**

- `assets/templates/app.json.template`
- `assets/templates/eas.json.template`
- `assets/templates/CLAUDE.md.template`
- `assets/templates/Makefile.template`
- `assets/templates/smoke-test.sh.template`
- `assets/templates/supabase-client.ts.template`
- `assets/templates/mcp-client.ts.template`

**Scripts to include.**

- `scripts/scaffold.ps1` - takes app name and bundle ID, outputs full project tree
- `scripts/verify-scaffold.ps1` - post-scaffold check that every required file exists

**Test cases for evals/evals.json.**

1. "Scaffold a mobile app called FloodPulse Mobile with bundle ID com.aignite.floodpulse"
2. "Start a new React Native project that talks to my Beacon GoM MCP server"
3. "Build me a mobile app boilerplate for tracking compliance"

## Skill 2: mvp-design-framework

**Purpose.** Force the five-step MVP discipline from the tutorial before any code is written. Core function, core loop, accessory features, surface area check, retention hook.

**Triggers on.** "Design a new app", "MVP", "app idea", "scope a mobile app", "feature plan", "what should this app do", "help me design", "design framework".

**Behavior.** When triggered, the skill asks Nuwan five questions in sequence and refuses to proceed until each is answered. After all five, it outputs a one-page MVP spec in markdown that becomes the input to mobile-app-scaffold.

The five questions, in order, exactly as written:

1. "What is the one thing this app does that, if removed, would mean the app is no longer the app?"
2. "What is the action the user takes, and the visual or haptic reward they get, inside thirty seconds of opening the app?"
3. "What three accessory features support that core loop without bloating it?"
4. "Count the screens. If the answer is more than seven, what cuts?"
5. "What unfinished state pulls the user back tomorrow?"

**Output format.** A markdown file called `MVP_SPEC.md` placed in the current project root. The file template is in `assets/templates/MVP_SPEC.md.template`.

**Hard constraint.** The skill must reject any MVP with more than seven screens. It must also reject any MVP where the retention hook is "push notifications" with no specifics. Push notifications are a channel, not a hook. Force the user to name what specific unfinished state the notification refers to.

**Reference files to include.**

- `references/why-this-framework.md` - the reasoning from the tutorial
- `references/examples.md` - three worked examples: habit tracker, calorie tracker, pomodoro

**Test cases for evals/evals.json.**

1. "I want to build a water intake tracker"
2. "Help me scope a mobile app for tracking my Texas highway construction bids"
3. "Design an app that turns RegScope alerts into a phone notification"

## Skill 3: supabase-bootstrap

**Purpose.** Stand up a Supabase project, generate a schema with RLS on by default, verify table count, and produce an API contract document. All in one command.

**Triggers on.** "Add a database", "Supabase setup", "auth setup", "database for my app", "set up Postgres", "add user accounts", "wire up Supabase".

**Behavior.**

1. Ask for project name and the Hostinger VPS region that is closest to users
2. Generate the schema file from a template plus user-specified tables
3. Apply RLS policies that default to authenticated-user-can-only-see-own-rows
4. Run the migration via Supabase CLI
5. Count tables before and after. If the count does not match expected, abort and dump the error
6. Generate `API_CONTRACT.md` listing every endpoint the frontend will call mapped to the backend route
7. Disable email confirmation in dev, keep it on in production
8. Output the project URL, anon key, and service role key to `.env.local` and to a 1Password entry if the user has 1Password CLI installed

**Critical rule.** Never skip the table count verification. The GoviHub post-mortem is in the skill's reference file as a permanent reminder.

**Reference files to include.**

- `references/rls-patterns.md` - common Row Level Security policies for AiGNITE products
- `references/govihub-postmortem.md` - five-day outage caused by silent migration failure
- `references/schema-patterns.md` - schemas for habits, completions, challenges, users, plus the AiGNITE three-tier intelligence pattern

**Asset files to include.**

- `assets/templates/schema.sql.template`
- `assets/templates/rls-defaults.sql`
- `assets/templates/API_CONTRACT.md.template`

**Scripts to include.**

- `scripts/bootstrap.ps1` - the main entry point
- `scripts/verify-tables.ps1` - counts tables, compares to expected
- `scripts/generate-contract.ps1` - reads schema, generates contract doc

**Test cases for evals/evals.json.**

1. "Add a database to my FloodPulse mobile app with tables for alerts, subscriptions, and user preferences"
2. "Set up Supabase auth for this project"
3. "Wire up the database for a habit tracker with five tables"

## Skill 4: security-audit

**Purpose.** Run the three-pass security audit on any project before deployment. Identify, fix, then re-audit to catch regressions introduced by the fix.

**Triggers on.** "Security audit", "pre-deploy check", "is this safe to ship", "check for vulnerabilities", "security review", "audit my app".

**Behavior.**

1. Pass one. Run the full security check against the codebase. Produce a tier list of findings tagged Critical, High, Medium, Low with CWE references.
2. Implement fixes for all Critical and High items. Any Medium and Low items get fixed only if the user opts in.
3. Pass two. Run the full check again from a fresh context. Confirm that no new vulnerabilities were introduced by the fixes. Compare to pass one.
4. Pass three. If pass two surfaced anything new, fix it, then run one final check.
5. Output `SECURITY_AUDIT.md` with the full trail.

**Checks the skill runs.**

- Hard-coded secrets in source
- Exposed environment variables in client bundles
- Missing server-side validation on API routes
- Default-open database policies
- Missing or inconsistent auth middleware
- Hallucinated package imports
- Console logs that leak request bodies or tokens
- Rate limiting on expensive operations
- CORS misconfigurations
- SQL injection patterns in raw queries
- XSS in user-supplied content paths

**Reference files to include.**

- `references/vulnerability-patterns.md` - the full taxonomy with examples
- `references/aignite-security-baseline.md` - what AiGNITE products must meet before launch
- `references/cwe-reference.md` - the CWE codes the skill cites

**Asset files to include.**

- `assets/templates/SECURITY_AUDIT.md.template`

**Scripts to include.**

- `scripts/run-audit.ps1` - the three-pass driver
- `scripts/scan-secrets.ps1` - grep for common secret patterns

**Test cases for evals/evals.json.**

1. "Run a security audit on my FloodPulse mobile app"
2. "Is this safe to ship to TestFlight"
3. "Check this project for vulnerabilities before I push to Apple"

## Skill 5: design-from-mockup

**Purpose.** Take any reference image, mockup, or screenshot and produce a pixel-close mobile UI inside an existing Expo project. Pipeline: extract assets, remove backgrounds, apply to scaffold, screenshot loop until match.

**Triggers on.** "Design like this", "match this style", "build from screenshot", "make it look like", "I want this design", "use this mockup", "copy this layout".

**Behavior.**

1. Accept input as either a local image path or a URL or a Gemini Imagegen prompt
2. If the input is a prompt, call the gemini-imagegen skill to produce four mockup variations
3. Extract assets from the chosen mockup: icons, illustrations, backgrounds
4. Remove backgrounds via Gemini edit pipeline
5. Apply assets to the project at the correct paths
6. Open the running Expo dev server in Chrome DevTools MCP
7. Screenshot, compare to mockup, identify deltas
8. Loop with prompts to Claude Code until the diff is below a threshold or the user accepts

**Critical rule.** Do not generate assets in a grid. Generate each asset one at a time with explicit "transparent background, no padding, single subject" prompts. The tutorial's grid approach forces Claude to crop, which is unreliable.

**Reference files to include.**

- `references/asset-extraction.md` - the one-at-a-time generation rule and why
- `references/screenshot-loop.md` - how to use Chrome DevTools MCP for visual verification
- `references/design-tokens.md` - AiGNITE default color palettes, fonts, spacing

**Asset files to include.**

- `assets/prompts/mockup-generation.txt` - Gemini Imagegen prompt template
- `assets/prompts/asset-extraction.txt` - asset isolation prompt template

**Scripts to include.**

- `scripts/extract-assets.ps1` - calls Gemini, removes backgrounds, places files
- `scripts/screenshot-compare.ps1` - drives the visual diff loop

**Test cases for evals/evals.json.**

1. "Design my FloodPulse mobile app to look like the Calm app onboarding"
2. "Match this Dribbble mockup for my habit tracker"
3. "Generate a high-end design for a Vedic astrology compatibility app"

## Skill 6: three-tier-test

**Purpose.** Enforce the Chrome to mirror to phone testing sequence with checkpoints. Each layer must pass before the next runs.

**Triggers on.** "Test my app", "verify the build", "is this ready to ship", "run the test suite", "QA the mobile app", "three-tier test".

**Behavior.**

1. Tier one. Chrome. Boot the Expo web build, run smoke tests via Playwright, verify every screen renders without console errors, verify every API call returns a 2xx
2. Tier two. iPhone Mirroring or Android emulator. Use the Expo development build, run a recorded UI walkthrough, capture screen video
3. Tier three. Physical device. Generate a QR code, open in Expo Go, run a manual checklist the user ticks off
4. Each tier writes a pass or fail to `TEST_RESULTS.md`
5. The skill refuses to mark a build "ready" unless all three tiers pass

**Integration.** Hooks into the smoke test produced by mobile-app-scaffold. Both must use the same endpoint list.

**Reference files to include.**

- `references/why-three-tiers.md` - what each tier catches that the others miss
- `references/playwright-setup.md` - how to wire Playwright into an Expo web build
- `references/physical-device-checklist.md` - the manual checks that only matter on real hardware

**Asset files to include.**

- `assets/templates/TEST_RESULTS.md.template`
- `assets/templates/manual-checklist.md.template`

**Scripts to include.**

- `scripts/run-tier-one.ps1`
- `scripts/run-tier-two.ps1`
- `scripts/run-tier-three.ps1`

**Test cases for evals/evals.json.**

1. "Run the three-tier test on my Cal Tracker app"
2. "Verify my FloodPulse mobile build before I submit"
3. "Is the pomodoro app ready to ship"

## Skill 7: app-store-submission

**Purpose.** Run the full EAS Submit pipeline. Generate privacy policies, host them on contact.aigniteconsulting.ai, produce required screenshots, fill App Store Connect metadata.

**Triggers on.** "Submit to App Store", "publish my app", "release to TestFlight", "push to Apple", "Google Play submission", "EAS submit".

**Behavior.**

1. Verify the build is ready. Refuse if three-tier-test has not passed in the last seven days.
2. Generate or update the privacy policy markdown. Push it to the AiGNITE marketing site via the Resend-verified domain.
3. Generate the support page if missing.
4. Run EAS build in production mode for the target platform.
5. Generate required screenshots in all sizes Apple needs. Use the running app on iPhone Mirroring.
6. Fill App Store Connect metadata from a YAML config: name, subtitle, description, keywords, category, age rating.
7. Create the test reviewer account in Supabase and add credentials to the submission notes.
8. Run `eas submit -p ios` or `eas submit -p android`.
9. Print the App Store Connect deep link for the user to finish the submission.

**Reference files to include.**

- `references/apple-checklist.md` - every requirement Apple enforces
- `references/google-checklist.md` - Google Play requirements
- `references/privacy-policy-template.md` - AiGNITE standard privacy language

**Asset files to include.**

- `assets/templates/privacy-policy.md.template`
- `assets/templates/support-page.md.template`
- `assets/templates/app-store-metadata.yaml.template`
- `assets/templates/screenshot-spec.md`

**Scripts to include.**

- `scripts/submit-ios.ps1`
- `scripts/submit-android.ps1`
- `scripts/generate-screenshots.ps1`
- `scripts/publish-privacy-policy.ps1`

**Test cases for evals/evals.json.**

1. "Submit my Cal Tracker app to TestFlight"
2. "Publish FloodPulse to the App Store"
3. "Push the pomodoro app to Google Play"

## Skill 8: mcp-to-mobile

**Purpose.** This is the flagship. Take any AiGNITE MCP server URL, read its available tools, and scaffold a full React Native app with one screen per tool, Supabase auth, push notifications, and Stripe subscription billing. Converts B2B MCP infrastructure into B2C revenue without rebuilding the backend.

**Triggers on.** "Turn this MCP into an app", "wrap my MCP server as a mobile app", "build a consumer app for [MCP name]", "mobile front end for FloodPulse", "consumer app from MCP", "MCP to mobile".

**Behavior.**

1. Ask the user for the MCP server URL or one of the AiGNITE shortcuts: beacon-gom, regscope, recallwatch, floodpulse, airshield, cosmic-nexus
2. Call the MCP server's tool discovery endpoint. List every tool the server exposes.
3. Ask the user to pick which tools become user-facing screens. Default to all read tools.
4. Generate the app via mobile-app-scaffold with a pre-filled name and bundle ID.
5. For each chosen tool, generate a screen that calls the tool via the MCP client, displays results in a card layout, and supports the tool's input parameters via a form.
6. Wire push notifications. For alert-style MCPs like FloodPulse, subscribe the device to a topic. For request-response MCPs like Cosmic Nexus, send a notification when the user's report is ready.
7. Wire Stripe. Free tier gets the first three queries per day. Paid tier removes the limit. Use the AiGNITE Stripe product templates.
8. Run supabase-bootstrap for the user accounts and subscription tracking.
9. Run security-audit.
10. Run three-tier-test.
11. Offer to run app-store-submission.

**Critical rule.** The MCP client in the mobile app must never expose the MCP server's admin tools. Filter the tool list to read-only and explicitly safe-for-public tools. The skill maintains a whitelist per AiGNITE MCP server.

**Reference files to include.**

- `references/aignite-mcp-catalog.md` - every AiGNITE MCP server, its public URL, its tool list, and the public-safe subset
- `references/mcp-client-patterns.md` - how to call MCP tools from React Native
- `references/stripe-tiers.md` - the AiGNITE default subscription tiers
- `references/push-notification-patterns.md` - alert subscriptions versus ready-notifications

**Asset files to include.**

- `assets/templates/screen-from-tool.tsx.template` - the per-tool screen scaffold
- `assets/templates/subscription-gate.tsx.template`
- `assets/templates/mcp-tool-form.tsx.template`

**Scripts to include.**

- `scripts/discover-tools.ps1` - hits the MCP server, lists tools
- `scripts/generate-screens.ps1` - generates one screen per chosen tool
- `scripts/wire-subscriptions.ps1` - sets up Stripe and Supabase subscription tables

**Test cases for evals/evals.json.**

1. "Turn FloodPulse into a mobile app for Houston residents"
2. "Build a consumer app from RegScope for compliance officers"
3. "Wrap my Cosmic Nexus MCP as a Vedic compatibility app for the App Store"

## Build Procedure for Each Skill

Repeat this loop for each of the eight skills. Do not move to skill N+1 until skill N is installed and a basic trigger test passes.

### Step 1. Create the skill directory

```powershell
$skillName = "mobile-app-scaffold"  # change per skill
$skillDir = "E:\AiGNITE\projects\custom-skills\$skillName"
New-Item -ItemType Directory -Path $skillDir -Force
New-Item -ItemType Directory -Path "$skillDir\references" -Force
New-Item -ItemType Directory -Path "$skillDir\scripts" -Force
New-Item -ItemType Directory -Path "$skillDir\assets" -Force
New-Item -ItemType Directory -Path "$skillDir\assets\templates" -Force
New-Item -ItemType Directory -Path "$skillDir\evals" -Force
```

### Step 2. Write SKILL.md

Frontmatter first. Description must be pushy and keyword-dense. Body must follow the writing style guide in the Mission section. Keep under 500 lines. If you approach 500 lines, push content into `references/` and link to it.

### Step 3. Write references

One file per logical reference area. Each reference file gets a one-line summary at the top so Claude knows whether to load it. Reference files can be longer than SKILL.md because they are loaded on demand.

### Step 4. Write assets

Templates use placeholder syntax `{{VARIABLE_NAME}}` for substitution. Scripts in `scripts/` do the substitution.

### Step 5. Write scripts

PowerShell scripts for Windows-native operations. Python scripts for cross-platform tasks. Every script must accept `-WhatIf` or `--dry-run`. Every script must exit non-zero on failure.

### Step 6. Write evals/evals.json

Three test prompts per skill. Format:

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

### Step 7. Write README.md

For the repo, not for Claude. Brief: what the skill does, how to install it manually, where to find more docs. This is what someone browsing the GitHub repo sees.

### Step 8. Install the skill

Copy the skill folder to the user-level Claude skills directory.

```powershell
$sourceDir = "E:\AiGNITE\projects\custom-skills\$skillName"
$targetDir = "$env:USERPROFILE\.claude\skills\$skillName"

if (Test-Path $targetDir) {
    Remove-Item -Recurse -Force $targetDir
}

Copy-Item -Recurse -Path $sourceDir -Destination $targetDir
Write-Host "Installed $skillName to $targetDir"
```

### Step 9. Verify the install

Open a fresh Claude Code session in a scratch directory and send the first test prompt from `evals/evals.json`. Confirm the skill triggers. If it does not trigger, the description is too weak. Make it pushier and re-test.

```powershell
# In a new terminal
cd $env:TEMP
mkdir claude-skill-test
cd claude-skill-test
claude
# Then paste the first eval prompt
```

### Step 10. Commit and tag

After all eight skills install and verify, initialize the custom-skills folder as a git repo, commit, and tag v0.1.0.

```powershell
cd E:\AiGNITE\projects\custom-skills
git init
git add .
git commit -m "Initial AiGNITE skills suite v0.1.0"
git tag v0.1.0
```

## Repo-Level Files

In addition to the eight skill folders, create these at the root of `E:\AiGNITE\projects\custom-skills`.

**README.md.** Sales-ready overview of the suite. Who it is for. What it does. How to install. Link to each skill's README.

**LICENSE.** MIT or proprietary, ask the user which.

**INSTALL.ps1.** Single script that copies all eight skills into the user's Claude skills directory in one shot.

**UPDATE.ps1.** Pulls the latest from this repo and re-installs.

**CHANGELOG.md.** Start at v0.1.0.

**docs/architecture.md.** How the eight skills compose. The dependency graph. Why they were built in this order.

**docs/skill-development.md.** How to add a ninth skill. Standards to follow. The writing style guide reproduced in full.

## Quality Gates Before Declaring Done

Run through this checklist. Every item must pass.

- All eight skills exist in `E:\AiGNITE\projects\custom-skills`
- All eight skills installed to `%USERPROFILE%\.claude\skills`
- Each skill has SKILL.md with valid YAML frontmatter
- Each skill has at least three test prompts in evals/evals.json
- Each skill triggers on the first test prompt in a fresh Claude Code session
- No em dashes anywhere in user-facing skill output
- No words from the avoid list appear in SKILL.md bodies
- The repo has a top-level README that sells the suite
- INSTALL.ps1 successfully installs all eight skills on a clean machine
- Git initialized, v0.1.0 tagged

## What to Do When You Hit Friction

If a skill fails to trigger, the description is the only thing that needs fixing. Read the skill-creator notes on triggering: simple one-step queries do not trigger skills regardless of description quality. Substantive queries do. Make the test prompt substantive.

If a script fails on Windows, check PowerShell execution policy. The user is on a Hostinger VPS workflow but local dev is Windows. Account for both.

If a reference file grows past 300 lines, add a table of contents at the top.

If you find yourself writing the same boilerplate across multiple skills, extract it to a shared reference and point both skills at it.

If anything in this brief contradicts the engineering standards in the Mission section, the engineering standards win.

## Final Output

When done, present a summary table to the user:

| Skill | Status | Install Path | Triggers Verified |
|-------|--------|--------------|-------------------|
| mobile-app-scaffold | Built and installed | ~/.claude/skills/mobile-app-scaffold | Yes |
| ... | ... | ... | ... |

Then ask if they want to add the suite to a private GitHub repo, publish to a public repo for the training market, or hold for further iteration.

Now begin. Start with mobile-app-scaffold and work through in order.
