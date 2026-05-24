# Lessons captured — Hermes VPS deploy

Compiled from the first reference run (srv453405 / aignite-web, Hostinger
KVM 4, May 2026). Every entry here cost real time to discover. Re-read this
file when something in the playbook seems wrong before deviating.

## 1. ONE container, not two

The prompt-template that drove the original install asked for a `gateway`
service and a separate `dashboard` service. **This is wrong.** The official
[Hermes docker user guide](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
says:

> The built-in web dashboard runs as an optional side-process inside the same
> container as the gateway. Set `HERMES_DASHBOARD=1` and expose port 9119 alongside
> the gateway's 8642.
>
> The dashboard side-process is not supervised — if it crashes, it stays down
> until the container restarts. Running it as a separate container is not
> supported: the dashboard's gateway-liveness detection requires a shared PID
> namespace with the gateway process.

If you try splitting, the dashboard reports the gateway as offline forever.
There is no workaround at the Hermes level.

## 2. There is NO native dashboard password

There is no `HERMES_WEBUI_PASSWORD` env var. The dashboard runs in `--insecure`
mode whenever bound to non-localhost (the entrypoint auto-adds the flag based
on `HERMES_DASHBOARD_HOST`). The docs explicitly warn:

> `--insecure` Allow binding to non-localhost (DANGEROUS: exposes API keys on
> the network)

So the actual auth model for a public install is **single-layer Traefik
basic-auth**. The bcrypt hash + 32-char random password is genuinely strong,
but you must be honest with the user that the dashboard itself has no internal
gate.

## 3. The `gateway` subcommand is for messaging gateways, not an HTTP API

`hermes gateway run` is for Telegram / Discord / WhatsApp / Slack / Weixin
integrations. The port 8642 it opens is the gateway's OpenAI-compatible API
server, which is **disabled by default** — exposing it requires:

```
API_SERVER_ENABLED=true
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<min 8 chars; generate with openssl rand -hex 32>
```

For a pure WebUI install (this skill's default), you do NOT publish or route
to 8642 at all. Only :9119 (dashboard) needs Traefik routing. The reason we
still use `gateway run` as the foreground command (not `dashboard --host
0.0.0.0`) is that the dashboard's liveness probe wants the gateway process
alive in the same PID namespace.

## 4. Default model goes in config.yaml, not .env

The current Hermes versions ignore `LLM_MODEL` in .env. From the bundled
`.env.example`:

> Default model is configured in `~/.hermes/config.yaml` (`model.default`).
> `LLM_MODEL` is no longer read from `.env` — this line is kept for reference
> only.

For per-invocation overrides, env vars `HERMES_INFERENCE_MODEL` and
`HERMES_INFERENCE_PROVIDER` work. For the persistent default, either edit
config.yaml or run `hermes model` / `hermes setup model` inside the container.
Easiest path: have the user pick from the dashboard's Settings → Models UI
after install.

## 5. Skill-sync prelude runs on every container start

The entrypoint runs `python3 /opt/hermes/tools/skills_sync.py` to refresh ~87
bundled skills on every boot. This adds ~10s to startup. The dashboard's web
build (Vite + npm) adds another ~30s on first boot.

Therefore the healthcheck **`start_period` must be ≥ 60s, preferably 90s**.
A shorter start_period causes spurious unhealthy → restart loops on slower
disks.

## 6. The compose file shipped inside the image is dashboard-only

```bash
docker run --rm --entrypoint cat nousresearch/hermes-agent:latest /opt/hermes/docker-compose.yml
```

…returns a minimal example with `command: ["dashboard", "--host",
"127.0.0.1", "--no-open"]`. This is NOT the deploy reference. The canonical
production compose is in the user-guide docs. Always fetch the docs, never
trust the in-image template.

## 7. Compose `$$` doubling — the only quoting gotcha that works

Traefik's basic-auth label value is `nuwan:$2y$05$DH...` — htpasswd bcrypt
output containing literal `$` chars. Compose interpolates `$VAR`, so any `$`
in a string is treated as variable expansion. The fix:

```bash
HASH_ESCAPED=$(htpasswd -nbB user pass | sed 's/\$/\$\$/g')
```

After `docker compose up`, **verify the actual container label** has single
`$` chars:

```bash
docker inspect hermes --format '{{index .Config.Labels "traefik.http.middlewares.hermes-auth.basicauth.users"}}'
# expect: nuwan:$2y$05$DHEv...   (single $)
```

Note: `docker compose config` **shows the value with `$$` still doubled** —
that's a display artifact of the YAML config output, NOT the runtime label.
Always verify via `docker inspect`.

## 8. `docker exec` defaults to root — and breaks state-writing subcommands

The container drops privileges to UID 10000 (`hermes` user) for the running
gateway. But `docker exec hermes ...` starts a new process as root by default,
which writes files as root-owned. The gateway (running as hermes) then cannot
read those files.

Concrete bug we hit: `docker exec hermes hermes pairing approve telegram <code>`
wrote `/opt/data/pairing/telegram-approved.json` as root:root mode 600. The
gateway reported the user as unauthorized for every subsequent message, even
after a restart — because the file was unreadable.

**Skill rule**: any `docker exec` against the Hermes container that writes
state files MUST use `docker exec -u hermes`. This applies to: `pairing
approve`, `mcp add`, `model`, `auth add`, anything that mutates files under
/opt/data.

## 9. Traefik integration — discover, don't assume

Per-VPS variations:

- **Network name**: was `traefik_network` on the Hostinger Docker+Traefik
  template. Other templates use `web`, `proxy`, `traefik`, `external`. ALWAYS
  discover via `docker inspect <traefik_container>`.
- **Cert resolver name**: was `letsencrypt` here. Could be `myresolver`,
  `prod`, `acme`. Discover from an existing routed service's labels (any
  `traefik.http.routers.X.tls.certresolver=Y` label).
- **Traefik API on :8080**: had `--api.insecure=false`, so the public REST
  endpoint wasn't queryable for naming conflicts. Not blocking — just pick a
  unique router name (`hermes`) and verify via `docker inspect` after `up`.
- **Provider mode**: the reference VPS had BOTH `--providers.docker=true` and
  `--providers.file.directory=/etc/traefik/config`. The skill uses Docker
  labels exclusively; file-provider isn't needed.

## 10. Env var names that match prompt exactly (no correction needed)

- `OPENROUTER_API_KEY` — correct per .env.example
- `HERMES_DASHBOARD` — correct, accepts `1`/`true`/`yes` case-insensitive
- `HERMES_DASHBOARD_HOST` — correct, default `0.0.0.0`
- `HERMES_DASHBOARD_PORT` — correct, default `9119`
- `HERMES_DASHBOARD_TUI` — correct, set to `1` to expose the embedded chat tab

## 11. Failure modes that the strict smoke test catches

- **TLS chain leaf-only**: `Verification: OK` AND chain depth ≥ 2 ensures the
  Let's Encrypt intermediate is being served. A common misconfiguration ships
  only the leaf cert; `curl -k` would pass it, real browsers/clients reject.
- **ACME challenge port blocked**: if `:80` inbound is firewalled, Let's
  Encrypt can't complete the HTTP-01 challenge. Traefik logs show the failure
  but the container still runs (no cert, no 200).
- **Wrong cert resolver name**: Traefik silently uses no cert. The smoke test
  catches this (404 on :443 instead of 401, or cert mismatch).
- **DNS not propagated**: external resolver check (`nslookup ... 8.8.8.8`)
  catches local-resolver poisoning vs real-world resolution.

## 12. Hostinger snapshot via API

If you have Hostinger API credentials and the VPS is on Hostinger, take a
snapshot before any irreversible change:

```python
# via MCP, if mcp__hostinger-api__ is connected
mcp__hostinger-api__VPS_createSnapshotV1(virtualMachineId=<id>)
# returns an action id; poll mcp__hostinger-api__VPS_getActionDetailsV1 until state=success
```

Snapshots take ~10 seconds and serve as the rollback path for anything that
goes wrong in Phase 5–6. If no Hostinger API available, log
`SNAPSHOT_UNAVAILABLE` in the audit trail and proceed — the user accepts the
risk by invoking the skill without one.

## 13. Things that worked exactly as the prompt described (positive lessons)

- Image name: `nousresearch/hermes-agent:latest` is correct (74 stars, 1.5M
  pulls on Docker Hub as of the reference run).
- Ports: 9119 (dashboard) and 8642 (gateway) match the docs.
- The `gateway run` foreground command works even with no messaging platform
  configured — it just logs "No messaging platforms enabled" and the dashboard
  remains the only entry point. Hermes does NOT exit; this is fine for a
  WebUI-only install.

## 14. Failure modes prepared for that didn't happen

These are still worth keeping as conditional branches in the skill for
future installs:

- ACME rate limit (50 certs/week per registered domain) — wasn't hit because
  this was the first `hermes.*` cert on the account. Future deploys to the
  same parent domain could hit it.
- Image pull failure / Docker Hub regional block — fall back to `ghcr.io`
  mirror if it exists (currently `ghcr.io/nousresearch/hermes-agent` returns
  401, so no fallback yet, but worth probing if Docker Hub fails).
- Existing container named `hermes` on the box — the skill should bail with a
  clear error rather than overwriting. The `install.sh` checks for this and
  warns but continues; tighten if you want strict mode.
