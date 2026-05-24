# Hermes follow-on extensions

These are optional add-ons that depend on a working core install (the WebUI is
up, Traefik basic-auth gates it, the container is healthy). The core skill
does NOT touch any of these — invoke this reference only when the user
explicitly asks for one of them.

## Anthropic OAuth — use your Claude subscription instead of OpenRouter

Most Claude Pro / Max subscribers should use Anthropic OAuth instead of
paying OpenRouter per-token. Their subscription includes a usage quota that
the agent can draw from.

**Dashboard route (preferred — user can do this themselves):**
1. Dashboard → **Settings** → **Providers** (or **Auth**)
2. **Add provider** → **Anthropic** → choose **Subscription / OAuth**
3. The dashboard opens a Claude.ai activation page in a new tab with a device
   code. Approve in browser (must be logged into Claude.ai).
4. Model Settings → CHANGE → pick a Claude model under the new `anthropic`
   provider (not under `openrouter`).

**CLI fallback (if dashboard doesn't surface OAuth):**
```bash
ssh "$SSH_ALIAS" "docker exec -u hermes -it hermes /opt/hermes/.venv/bin/hermes login anthropic"
```
Prints a device code + URL; user approves in browser; CLI completes; refresh
token written to `/opt/data/auth.json` (which the entrypoint handles for
first-boot bootstrap via `HERMES_AUTH_JSON_BOOTSTRAP`).

After OAuth is wired, the `OPENROUTER_API_KEY` line in `/opt/data/.env` can
be removed if the user wants to stop paying OpenRouter.

**Recommend a fallback chain** for resilience when the primary model is rate-
limited or overloaded:
- Dashboard → Model Settings → Fallback → add `anthropic/claude-haiku-4.5`
  (still subscription)
- Optionally also add `openrouter/anthropic/claude-sonnet-4.5` as a paid
  fallback if `OPENROUTER_API_KEY` is configured.

## Telegram pairing

Wire a Telegram bot so the user can talk to Hermes from their phone.

### Setup (user must do step 1)

1. **User creates a bot in Telegram via @BotFather**, copies the bot token.
2. Add the token to `/opt/hermes/data/.env`:
   ```
   TELEGRAM_BOT_TOKEN=<token from BotFather>
   ```
3. **Important**: `env_file` is read at container CREATION, not at restart.
   To pick up the new env var, use `docker compose up -d` (not `restart`).
   ```bash
   ssh "$SSH_ALIAS" "cd /opt/hermes && docker compose up -d"
   ```
4. Wait for healthy. The gateway log should drop the "No messaging platforms
   enabled" warning — confirming Telegram is connected.

### First-message pairing

5. User opens https://t.me/<bot_username> in browser (Telegram in-app search
   for new bots is flaky — use the deep link). Hits **Start**, sends "hi".
6. The bot replies with a pairing code:
   ```
   Hi~ I don't recognize you yet!
   Here's your pairing code: <CODE>
   Ask the bot owner to run:
   hermes pairing approve telegram <CODE>
   ```
7. **MUST use `-u hermes` here** (see lessons.md § 8):
   ```bash
   ssh "$SSH_ALIAS" "docker exec -u hermes hermes /opt/hermes/.venv/bin/hermes pairing approve telegram <CODE>"
   ```
8. Restart container so the gateway re-reads the pairing allowlist:
   ```bash
   ssh "$SSH_ALIAS" "cd /opt/hermes && docker compose restart"
   ```
9. User sends another message — should get a real agent response now.

### "Set home channel" prompt

When the bot first chats with the user, it asks: *"No home channel is set for
Telegram. Type /sethome to make this chat your home channel."* For a solo
user with one chat, this is the right move — outgoing cron deliveries land in
that DM.

## MCP server wiring

Hermes supports MCP both ways: as a client (consumes external MCP tools) and
as a server (exposes itself to other clients via `hermes mcp serve`).

### Add an MCP server

```bash
ssh "$SSH_ALIAS" "
printf '\n\nY\n' | docker exec -i -u hermes hermes /opt/hermes/.venv/bin/hermes mcp add <name> --url '<url>'
"
```

The `printf '\n\nY\n' | docker exec -i` is required because `mcp add` is
interactive (asks "Does this server require authentication? [Y/n]", then "API
key / Bearer token:", then "Enable all N tools? [Y/n/select]"). Without stdin
piping, EOF cancels each prompt and the install aborts. `\n\nY\n` handles all
three prompts: blank for auth question (defaults to Y), blank for token (URL
token wins anyway), Y to enable all tools.

### Transport detection — known limitation

`hermes mcp add --url` auto-detects between `stdio` and streamable-HTTP, but
**does NOT auto-detect SSE** even when the URL ends in `/sse`. If you see:

```
✗ Failed to connect: Client error '405 Method Not Allowed' for url '<...>/sse'
```

…the server is SSE-only and Hermes is POSTing instead of GETting. Workaround:
hand-edit `/opt/data/config.yaml` to add `transport: sse` to the server entry:

```yaml
mcp_servers:
  <name>:
    url: https://<host>/mcp/sse?token=<token>
    transport: sse        # undocumented but honored by Hermes' MCP client
    enabled: true
```

After saving, run `hermes mcp test <name>` to verify the SSE handshake
succeeds.

### Verify a server's transport before adding

Probe with curl: if `GET <url>/sse` returns `content-type: text/event-stream`,
it's SSE-only and you need the `transport: sse` workaround. If `POST <url>`
returns a non-405 response, streamable-HTTP works via `mcp add --url`.

### Session reload required

After adding MCP servers, the running gateway and any active sessions do NOT
auto-pick up the new tools. The CLI says *"Start a new session to use these
tools."* For Telegram users, send `/new` in DM. For the dashboard chat tab,
open a fresh session. No container restart needed — this is a session-level
reload, not a process-level one.

## Gmail monitoring via himalaya cron

Multi-account inbox polling with rules-based classification and a single
silent-when-empty Telegram digest per cron run.

### Why IMAP + himalaya + cron (not Gmail Push)

Gmail Push requires a Google Cloud project, Pub/Sub topic, OAuth credentials
per account, a public webhook endpoint, and a daily `watch()` renewal cron.
It's the right architecture for sub-second latency. For 15-minute latency on
5 accounts, IMAP polling via the bundled `himalaya` CLI is dramatically
simpler.

### Setup

1. **Per-account: enable Gmail IMAP**:
   - User's Gmail → Settings → Forwarding and POP/IMAP → Enable IMAP, save
   - For Workspace accounts, admin must also enable IMAP at:
     Admin Console → Apps → Google Workspace → Gmail → End User Access →
     Enable IMAP access (this is org-level; user-level toggle is still
     required after).

2. **Per-account: generate an app password**:
   - 2-Step Verification must be ON
   - https://myaccount.google.com/apppasswords → name it "Hermes Email
     Monitor" → copy the 16-char string.
   - Workspace gotcha: log in as the **canonical primary address**, not an
     alias. Gmail IMAP rejects login attempts with alias addresses.

3. **Install himalaya inside container** (persists across recreates because
   `/opt/data` is bind-mounted; the container's PATH already includes
   `/opt/data/.local/bin`):
   ```bash
   ssh "$SSH_ALIAS" "docker exec -u hermes hermes bash -c '
     cd /tmp && curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh -o himalaya-install.sh && PREFIX=/opt/data/.local sh himalaya-install.sh
   '"
   ```

4. **Write multi-account himalaya config** at
   `/opt/data/.config/himalaya/config.toml` — one `[accounts.NAME]` block
   per Gmail account, all with `backend.host = "imap.gmail.com"`,
   `backend.port = 993`, `backend.encryption.type = "tls"`,
   `backend.auth.cmd = "cat /opt/data/.config/himalaya/passwords/NAME.txt"`.
   Also set `folder.aliases.sent = "[Gmail]/Sent Mail"` etc. — Gmail uses
   non-canonical folder names and v1.2.0+ himalaya needs the alias to save
   to Sent correctly.

5. **Write per-account password files** to
   `/opt/data/.config/himalaya/passwords/NAME.txt` (chmod 600, hermes-owned;
   spaces stripped from the displayed app password — Gmail accepts either
   form but no-space is safer).

6. **Write `email-poll.py`** to `/opt/data/scripts/email-poll.py` (see the
   reference deploy's script for the full implementation — it iterates
   accounts via `himalaya envelope list --output json`, dedups via a
   state file at `/opt/data/.config/himalaya/seen-uids.json`, classifies
   against blocklists, emits a Telegram-friendly digest or nothing).

7. **Create the cron job** in `--no-agent` mode so empty stdout = silent:
   ```bash
   ssh "$SSH_ALIAS" "docker exec -u hermes hermes /opt/hermes/.venv/bin/hermes cron create \
     'every 15m' \
     --name 'Gmail monitor' \
     --deliver telegram \
     --script email-poll.py \
     --no-agent"
   ```

   **Schedule gotcha**: `'15m'` (without `every`) means **one-shot in 15
   minutes**, not "every 15 minutes". Always use `'every 15m'` for recurring
   jobs.

### Classification design

Two-pass rules:
1. **Pass 1**: blocklist senders ALWAYS lose, even if the subject screams
   urgent. (Otherwise Patreon billing-reminder subjects like "Your
   memberships will be cancelled" hit the urgent regex and surface as false
   positives.)
2. **Pass 2**: if sender survived blocklist AND subject matches the urgent
   regex (urgent/asap/refund/dispute/invoice/contract/payment failed/etc.),
   promote to important.
3. **Default**: sender passed blocks but no urgent keyword → still treat as
   important (the user can see anything the rules let through; better to
   over-alert on real humans than miss).

### Verify himalaya can authenticate before going further

```bash
ssh "$SSH_ALIAS" "docker exec -u hermes hermes /opt/data/.local/bin/himalaya envelope list -a <account> --page-size 3"
```

If you see `AUTHENTICATIONFAILED`: (a) IMAP isn't enabled at user level,
(b) app password was mistyped — regenerate, (c) the email is an alias —
switch to the canonical primary address.

### Trigger the cron manually

```bash
ssh "$SSH_ALIAS" "
docker exec -u hermes hermes /opt/hermes/.venv/bin/hermes cron run <job_id>
docker exec -u hermes hermes /opt/hermes/.venv/bin/hermes cron tick
"
```
