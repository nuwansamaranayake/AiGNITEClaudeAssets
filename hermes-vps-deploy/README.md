# hermes-vps-deploy

A Claude Code skill that stands up [Hermes Agent](https://hermes-agent.nousresearch.com)
on any Linux VPS that already has Docker + Traefik running. Produces a working
WebUI at `https://hermes.<your-domain>` behind Traefik basic-auth + Let's Encrypt
TLS in ~5 minutes.

Built from a real reference deploy on Hostinger KVM 4 (Ubuntu 22.04 + Docker
29.5 + Traefik v2.11). Every lesson learned during that run is captured in
[references/lessons.md](references/lessons.md) so subsequent deploys don't
re-discover them.

## What it does

- Discovers the existing Traefik container, network, and cert resolver (does NOT
  hardcode names — these vary per VPS template).
- Pulls `nousresearch/hermes-agent:latest`.
- Generates a 32-char random Traefik basic-auth password, bcrypts it, and bakes
  the hash into a Traefik label on the container with correct `$$` escaping.
- Brings up ONE container running `hermes gateway run` with `HERMES_DASHBOARD=1`
  so the dashboard backgrounds as a side-process (the docs-approved pattern;
  splitting into two containers BREAKS the dashboard's gateway liveness probe).
- Runs strict smoke tests: external DNS, TLS chain verification (no `-k`), 401
  without creds, 200 with creds.
- Writes an audit trail, credentials file, and lessons file on the VPS.

## What it produces

After a successful run on `srv453405` (the reference deploy):

```
WebUI:        https://hermes.aigniteconsulting.ai
Credentials:  /root/hermes-credentials-<date>.txt   (chmod 600)
Audit:        /root/hermes-install-<date>.md         (every phase, every command)
Lessons:      /root/hermes-lessons-captured.md       (surprises + corrections)
Compose:      /opt/hermes/docker-compose.yml
Disk used:    ~6 GB (mostly the image + bundled Playwright/Chromium)
Container:    healthy in ~35s on first boot
```

## Install (Claude Code)

```bash
# Drop the skill directory into your global skills folder
mkdir -p ~/.claude/skills
cp -r hermes-vps-deploy ~/.claude/skills/

# In a Claude Code session
Skill(skill: "hermes-vps-deploy")
```

Then tell Claude: *"deploy hermes on aignite-web with subdomain hermes.example.com"*
— it will follow the playbook in `SKILL.md`.

## Quick mode (just run the installer)

If you don't need Claude in the loop:

```bash
export SSH_ALIAS=aignite-web
export HERMES_SUBDOMAIN=hermes.example.com
export TRAEFIK_BASIC_AUTH_USER=nuwan
export CONTAINER_CPU_LIMIT=2.0
export CONTAINER_MEMORY_LIMIT=4G
bash assets/install.sh
```

## Prerequisites

- VPS with Docker + an already-configured Traefik (v2 or v3) with a Let's Encrypt
  cert resolver and the Docker label provider enabled
- DNS A record for `hermes.<your-domain>` pointing at the VPS public IP
- An SSH alias in your `~/.ssh/config` that authenticates without a password
  prompt (key-based)
- Inbound :80 and :443 reachable from the public internet (ACME HTTP-01)

## What this skill does NOT do (yet)

- Wire up Telegram, Discord, WhatsApp, etc. (see
  [references/follow-on-extensions.md](references/follow-on-extensions.md))
- Configure MCP servers (also in follow-on-extensions.md)
- Set up Gmail monitoring (also in follow-on-extensions.md)
- Anthropic OAuth (user does this from the dashboard's Settings → Providers UI
  after install — takes 30 seconds and uses your Claude Pro/Max subscription
  instead of an OpenRouter key)

## Why one container, not two

The official Hermes docs are explicit: the dashboard cannot run in a separate
container. Its gateway-liveness detection needs a shared PID namespace with the
`gateway run` process. We tested splitting; it does not work. See
[references/lessons.md § 1](references/lessons.md) for the full story.

## License

MIT. Adapt freely.

## Credit

Reference deploy + skill packaging by Nuwan Samaranayake @ AiGNITE Consulting
(May 2026). Hermes Agent itself is by Nous Research —
https://github.com/NousResearch/Hermes-Agent.
