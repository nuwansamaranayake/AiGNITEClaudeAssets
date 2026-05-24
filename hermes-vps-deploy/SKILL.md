---
name: hermes-vps-deploy
description: Deploy Hermes Agent (Nous Research) to a Hostinger VPS (or any Linux box with Docker + Traefik already running) so that it serves a working WebUI dashboard at https://hermes.<domain> behind Traefik basic auth + Let's Encrypt TLS. Produces an audit trail, credentials file, and lessons file. Use this skill whenever the user says "deploy hermes", "install hermes agent", "set up hermes on my vps", "hermes nous research", "hermes web ui behind traefik", or any phrase that asks to stand up a Hermes Agent dashboard on a remote host. Optional add-ons (covered in references/follow-on-extensions.md): Anthropic OAuth via Claude subscription, Telegram pairing, MCP server wiring, Gmail monitoring via himalaya cron.
---

# Hermes VPS Deploy — runbook

This skill stands up [Hermes Agent](https://hermes-agent.nousresearch.com) on a
remote VPS, integrated with an existing Traefik reverse proxy. It is opinionated
about the design (one container, dashboard backgrounded via env var, Traefik
basic auth as the only auth layer) because every alternative was tested and
documented in `references/lessons.md` — read that file if anything in this
playbook seems wrong.

## When to use

User says any of:
- "deploy / install hermes (agent)"
- "stand up hermes on (my vps / hostinger / a server)"
- "hermes web ui behind traefik"
- "hermes nous (research)"
- "give me a hermes dashboard at <subdomain>"
- "follow the hermes skill"

## What this produces

By the end of a successful run:
- One Docker container named `hermes` running `nousresearch/hermes-agent:latest`
  with `gateway run`. The dashboard is backgrounded as a side-process via
  `HERMES_DASHBOARD=1`.
- Traefik routes `https://<subdomain>` → container:9119 with HTTPS via the
  existing Let's Encrypt resolver, behind a bcrypt basic-auth middleware.
- A credentials file at `/root/hermes-credentials-<date>.txt` (chmod 600) with
  the Traefik basic-auth password.
- An audit trail at `/root/hermes-install-<date>.md` with every Phase 0–7 step.
- A lessons-captured file at `/root/hermes-lessons-captured.md` (seed for
  iterating on this skill).
- The compose file at `/opt/hermes/docker-compose.yml`.

## Prerequisites (verify before invoking)

1. **DNS**: `<subdomain>` (e.g. `hermes.example.com`) must already resolve to
   the VPS's public IPv4.
2. **VPS access**: An SSH alias in `~/.ssh/config` that authenticates silently
   (key-based). Bare-IP SSH commands are forbidden by this skill — see
   `references/lessons.md` § SSH.
3. **Existing Traefik**: A Traefik container must be running on the VPS,
   listening on :80 and :443, with an ACME (Let's Encrypt) cert resolver
   configured and the Docker label provider enabled. The skill discovers the
   exact network name, container name, and resolver name — never assume.
4. **Disk and RAM**: At least 5 GB free disk and 2 GB free RAM. The image is
   ~3 GB; Playwright/Chromium browsers add ~1 GB.
5. **Inbound 80 + 443 reachable**: ACME challenge runs on :80. If the VPS sits
   behind a firewall that blocks :80 inbound, ACME will fail.

## Inputs the operator must collect before invoking

Ask the user for each, never invent:

| Variable | Example | Notes |
|---|---|---|
| `SSH_ALIAS` | `aignite-web` | Must be a working alias in `~/.ssh/config`. |
| `HERMES_SUBDOMAIN` | `hermes.aigniteconsulting.ai` | DNS already pointed at VPS. |
| `TRAEFIK_BASIC_AUTH_USER` | `nuwan` | Username for the basic-auth gate. |
| `INSTALL_DIR` | `/opt/hermes` | Almost always this. |
| `DATA_DIR` | `/opt/hermes/data` | Will become `HERMES_HOME=/opt/data` inside container. |
| `CONTAINER_CPU_LIMIT` | `2.0` | Tune for VPS plan (KVM 2 → 1.5, KVM 4 → 2, KVM 8 → 4). |
| `CONTAINER_MEMORY_LIMIT` | `4G` | Same. |
| `HOSTINGER_VPS_ID` | `453405` | Optional — only used to take a pre-install snapshot via Hostinger API. Skip if not Hostinger or no API key. |

## Hard rules (NEVER violate — these mistakes cost a day apiece in the reference run)

1. **One container, not two.** The Hermes design has a single container running
   `gateway run`; the dashboard is an unsupervised side-process started inside
   the same container via `HERMES_DASHBOARD=1`. Splitting them breaks the
   dashboard's gateway-liveness detection because it requires a shared PID
   namespace. The official docs explicitly say "Running it as a separate
   container is not supported."

2. **There is NO native dashboard password.** Setting any `HERMES_WEBUI_PASSWORD`
   env var does nothing. The dashboard's `--insecure` flag (auto-set by the
   entrypoint when binding non-localhost) only allows non-localhost binding; it
   does not gate access. Auth comes from Traefik basic-auth and that is the only
   layer. Tell the user this honestly when you summarize.

3. **Never use `curl -k` in the smoke tests.** A leaf-only cert chain will pass
   `-k` but break real browsers and clients. Use `openssl s_client` and grep for
   `Verification: OK` and chain depth ≥ 2.

4. **Always use the SSH alias.** Never `ssh root@<ip>`. The user's CLAUDE.md
   enforces this fleet-wide.

5. **Discover Traefik configuration; do not assume.** Network name, cert
   resolver name, and ACME storage path vary per VPS. Discover via
   `docker inspect` on the running Traefik container and any existing routed
   service. See Phase 1 below.

6. **For `$$` in compose label values containing bcrypt hashes**: htpasswd
   output contains literal `$` chars. Compose interpolates `$VAR`, so every `$`
   in the hash MUST be doubled to `$$` in the compose file. `docker compose
   config` will display the value with `$$` still doubled — that is a display
   artifact only. Verify the *actual* container label via
   `docker inspect hermes --format '{{json .Config.Labels}}'` after `up`; you
   should see single `$` chars in the bcrypt portion.

7. **`docker exec` defaults to root.** Any command run via `docker exec hermes
   ...` runs as root inside the container, even though the gateway runs as the
   non-root `hermes` user (UID 10000). Files written by root-mode exec become
   unreadable by the gateway. ALWAYS use `docker exec -u hermes hermes ...`
   when running any `hermes` subcommand that writes state (pairing approve,
   mcp add, model select, auth add, etc.).

## Phase 0 — Pre-flight

Open the audit log at `/root/hermes-install-<YYYY-MM-DD>.md` on the VPS. Append
every Phase's output via `tee -a`. Then verify:

```bash
ssh "$SSH_ALIAS" "bash -s" <<'PRE'
LOG=/root/hermes-install-$(date -u +%Y-%m-%d).md
exec > >(tee -a "$LOG") 2>&1
echo "## Phase 0 — Pre-flight ($(date -u +%FT%TZ))"
echo "hostname: $(hostname)"
echo "disk:"; df -h /
echo "ram:";  free -h
echo "docker version: $(docker --version)"
echo "containers running:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo "hermes leftovers (should all be empty):"
docker ps -a --format "{{.Names}}" | grep -i hermes || echo "(none)"
docker volume ls --format "{{.Name}}" | grep -i hermes || echo "(none)"
echo "DNS for the subdomain (should resolve to this VPS):"
getent hosts "${HERMES_SUBDOMAIN}"
echo "external resolver check:"
nslookup "${HERMES_SUBDOMAIN}" 8.8.8.8 | grep -E "Address|Name"
echo "port 80/443 baseline (expect 404 or 503 — Traefik reachable, no route yet):"
curl -sI -o /dev/null -w "HTTP :80 %{http_code}\n" "http://${HERMES_SUBDOMAIN}/"
curl -sI -o /dev/null -w "HTTPS :443 %{http_code}\n" -k "https://${HERMES_SUBDOMAIN}/"
PRE
```

ABORT if hostname doesn't match the expected VPS, if `/opt/hermes` already
exists (a previous install), or if DNS doesn't resolve to the VPS public IP.

Take a Hostinger snapshot if the API is available (`VPS_createSnapshotV1`).
Log `SNAPSHOT_UNAVAILABLE` and proceed if not. The user accepts the rollback
risk if you proceed without one.

## Phase 1 — Discover Traefik

Find the live Traefik container, network, cert-resolver name, and label
provider. Hardcoding fails on other VPSs.

```bash
ssh "$SSH_ALIAS" "bash -s" <<'D'
TRAEFIK=$(docker ps --format "{{.Names}}" | grep -i traefik | head -1)
echo "traefik_container=$TRAEFIK"

# Network — usually traefik_network or proxy or web; discover, do not assume
docker inspect "$TRAEFIK" --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}'

# Cert resolver name — discover from any existing routed service's labels
for c in $(docker ps --format "{{.Names}}" | grep -v -i traefik); do
  docker inspect "$c" --format '{{range $k, $v := .Config.Labels}}{{if and (eq (slice $k 0 8) "traefik.") (gt (len $k) 8)}}{{$k}}={{$v}}{{"\n"}}{{end}}{{end}}' 2>/dev/null | grep certresolver | head -1 && break
done

# ACME storage location (for diagnosing chain issues later)
find /opt /etc -maxdepth 5 -name acme.json 2>/dev/null
D
```

Persist three values: `TRAEFIK_NETWORK`, `CERT_RESOLVER_NAME` (almost always
`letsencrypt`), and `TRAEFIK_CONTAINER_NAME`. Append findings to the audit log.

## Phase 2 — Prepare host directories + secrets

```bash
ssh "$SSH_ALIAS" "bash -s" <<'S'
mkdir -p /opt/hermes /opt/hermes/data
chmod 755 /opt/hermes
chmod 700 /opt/hermes/data

which htpasswd >/dev/null 2>&1 || apt-get install -y apache2-utils >/dev/null 2>&1

TRAEFIK_BASIC_PASS=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
RAW_HASH=$(htpasswd -nbB "${TRAEFIK_BASIC_AUTH_USER}" "$TRAEFIK_BASIC_PASS")
HASH_ESCAPED=$(echo "$RAW_HASH" | sed 's/\$/\$\$/g')   # $$ for compose interpolation

cat > /root/hermes-credentials-$(date -u +%Y-%m-%d).txt <<EOF
HERMES INSTALL CREDENTIALS
============================
WebUI URL: https://${HERMES_SUBDOMAIN}
Traefik basic auth:
  Username: ${TRAEFIK_BASIC_AUTH_USER}
  Password: ${TRAEFIK_BASIC_PASS}
OpenRouter API key:  NOT CONFIGURED — user adds to /opt/hermes/data/.env if using OpenRouter; skip if using Anthropic OAuth
EOF
chmod 600 /root/hermes-credentials-*.txt

# Stash the escaped hash for the next phase
echo "$HASH_ESCAPED" > /opt/hermes/.basic_auth_hash_escaped
chmod 600 /opt/hermes/.basic_auth_hash_escaped
S
```

DO NOT echo the password into the audit log. Only log the file path.

## Phase 3 — Render docker-compose.yml

Use the template at `assets/docker-compose.template.yml`. Substitute:
- `<TRAEFIK_NETWORK>` → value from Phase 1
- `<CERT_RESOLVER_NAME>` → value from Phase 1
- `<HERMES_SUBDOMAIN>` → user input
- `<HTPASSWD_HASH_ESCAPED>` → file from Phase 2 (the `$$` doubled version)
- `<CPU_LIMIT>`, `<MEMORY_LIMIT>` → user input

Write the rendered compose to `/opt/hermes/docker-compose.yml`. Validate with
`docker compose -f /opt/hermes/docker-compose.yml config --quiet`.

## Phase 4 — Pre-populate .env

```bash
ssh "$SSH_ALIAS" "cat > /opt/hermes/data/.env" <<'ENV'
# Hermes Agent — environment configuration
# Set OPENROUTER_API_KEY here if using OpenRouter (then `docker compose restart`)
# OR skip and use Anthropic OAuth via dashboard Settings → Providers (recommended for Claude subscribers).
OPENROUTER_API_KEY=PLACEHOLDER_REPLACE_AFTER_INSTALL

# Dashboard exposure is set via docker-compose env block (HERMES_DASHBOARD=1).
ENV
ssh "$SSH_ALIAS" "chmod 600 /opt/hermes/data/.env"
```

The entrypoint copies `/opt/hermes/.env.example` to `/opt/data/.env` on first
boot if .env is missing. By pre-creating, our placeholder isn't overwritten.

## Phase 5 — Bring up

```bash
ssh "$SSH_ALIAS" "cd /opt/hermes && docker compose pull && docker compose up -d"
```

Poll for healthy (give it up to 180s — the entrypoint syncs 87 bundled skills
on first run which takes ~10s, then the dashboard builds web assets):

```bash
ssh "$SSH_ALIAS" "
for i in \$(seq 1 36); do
  s=\$(docker inspect hermes --format '{{.State.Health.Status}}' 2>/dev/null)
  printf 't=%3ds %s\n' \$((i*5)) \$s
  [ \"\$s\" = healthy ] && break
  [ \"\$s\" = unhealthy ] && { echo UNHEALTHY; docker logs --tail 80 hermes; exit 1; }
  sleep 5
done
"
```

After healthy, immediately verify the actual container label has single `$`
chars in the bcrypt hash (not `$$`):

```bash
ssh "$SSH_ALIAS" "docker inspect hermes --format '{{index .Config.Labels \"traefik.http.middlewares.hermes-auth.basicauth.users\"}}'"
```

You should see one `$` between bcrypt sections (e.g. `nuwan:$2y$05$...`). If
you see `$$`, the compose interpolation is broken — fix and re-up.

## Phase 6 — Smoke tests (STRICT — no `-k`)

```bash
ssh "$SSH_ALIAS" "bash -s" <<S
# Test 1: external DNS
nslookup ${HERMES_SUBDOMAIN} 8.8.8.8 | grep Address

# Test 2: TLS chain (no -k). Verify chain depth >= 2 and 'Verification: OK'
echo | openssl s_client -connect ${HERMES_SUBDOMAIN}:443 \
  -servername ${HERMES_SUBDOMAIN} 2>&1 | grep -E "Verification|depth=|subject="

# Test 3: HTTPS without creds (expect 401 from Traefik basic-auth challenge)
curl -sI --max-time 10 https://${HERMES_SUBDOMAIN}/ -o /dev/null -w "no-auth: %{http_code}\n"

# Test 4: HTTPS with creds (expect 200 from dashboard past Traefik)
PASS=\$(awk '/^  Password:/ {print \$2; exit}' /root/hermes-credentials-*.txt)
curl -s --max-time 10 -u "${TRAEFIK_BASIC_AUTH_USER}:\$PASS" https://${HERMES_SUBDOMAIN}/ \
  -o /dev/null -w "with-auth: %{http_code}\n"

# Test 5: cert details
echo | openssl s_client -connect ${HERMES_SUBDOMAIN}:443 \
  -servername ${HERMES_SUBDOMAIN} 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates
S
```

Pass criteria:
- DNS resolves to the VPS public IP
- TLS: `Verification: OK` AND chain depth ≥ 2 (leaf + intermediate)
- No-auth: 401
- With-auth: 200 (or 405 if HEAD is rejected — try GET to confirm)
- Cert: subject CN matches subdomain, issuer is Let's Encrypt, dates valid

If TLS verification fails, STOP. This is the Cosmic-Nexus leaf-only-cert trap.
Diagnose via:
```bash
docker logs <traefik_container> 2>&1 | grep -iE "acme|hermes|certificate" | tail -50
```
Common causes: port 80 not reachable externally, wrong cert resolver name, rate
limit hit. Snapshot rollback is the recovery path.

## Phase 7 — Summary + lessons

Append a final summary block to the audit log with pass/fail counts. Write the
lessons file at `/root/hermes-lessons-captured.md` documenting any surprises
encountered (env var name corrections, transport quirks, etc.). Pull the
compose file back to the local skill author's machine so the
template can be improved.

Print to the user:
```
INSTALLED — N/5 smoke tests pass
WebUI: https://${HERMES_SUBDOMAIN}
Credentials: /root/hermes-credentials-<date>.txt
Audit: /root/hermes-install-<date>.md

Next:
  1. Browse to the URL, authenticate with Traefik creds
  2. (Optional) Dashboard → Settings → Providers → Add Anthropic via Subscription / OAuth (recommended over OpenRouter for Claude Pro/Max subscribers)
  3. (Optional) See references/follow-on-extensions.md for Telegram pairing, MCP wiring, and Gmail monitoring
```

## Quick mode

The complete Phase 0–7 flow is also packaged as a shell script at
`assets/install.sh`. The script reads the required inputs from environment
variables (`SSH_ALIAS`, `HERMES_SUBDOMAIN`, `TRAEFIK_BASIC_AUTH_USER`, etc.)
and runs all phases unattended. Use this for repeat deploys; use the phase-by-
phase playbook above for the first deploy on a new VPS so you can pause at
each smoke test.

## When to read the references

- **Anything surprising** during Phase 1 discovery (wrong network name, missing
  cert resolver) → read `references/lessons.md` § Traefik.
- **Smoke test fails** → read `references/lessons.md` § Failure modes.
- **User asks about Telegram, MCP servers, or Gmail monitoring** → read
  `references/follow-on-extensions.md`. These extensions are NOT part of the
  core install; they're separate flows that depend on the base install.
- **User asks "why is X like this?"** → answer from `references/lessons.md` if
  available; otherwise be honest you don't know.
