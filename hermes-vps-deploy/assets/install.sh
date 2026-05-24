#!/usr/bin/env bash
# hermes-vps-deploy / install.sh
#
# Unattended Phase 0–7 installer. Reads inputs from env vars (see ENV block).
# Logs every step to /root/hermes-install-<date>.md on the VPS.
# Writes a credentials file at /root/hermes-credentials-<date>.txt (chmod 600).
#
# Designed to be idempotent for re-runs (skips work that's already done).
# If you want to start completely clean, run the cleanup section commented at
# the bottom of this file first.

set -euo pipefail

# ============================================================================
# ENV (must be set by caller)
# ============================================================================
: "${SSH_ALIAS:?Set SSH_ALIAS — must be a working alias in ~/.ssh/config}"
: "${HERMES_SUBDOMAIN:?Set HERMES_SUBDOMAIN (e.g. hermes.example.com)}"
: "${TRAEFIK_BASIC_AUTH_USER:?Set TRAEFIK_BASIC_AUTH_USER (e.g. nuwan)}"
: "${CONTAINER_CPU_LIMIT:=2.0}"
: "${CONTAINER_MEMORY_LIMIT:=4G}"
: "${INSTALL_DIR:=/opt/hermes}"
: "${DATA_DIR:=/opt/hermes/data}"

DATE=$(date -u +%Y-%m-%d)
LOG="/root/hermes-install-${DATE}.md"
CREDS="/root/hermes-credentials-${DATE}.txt"

ssh_run() { ssh "$SSH_ALIAS" "$@"; }
ssh_bash() { ssh "$SSH_ALIAS" bash -s; }

echo "==> Phase 0: pre-flight checks on $SSH_ALIAS"
ssh_bash <<PRE
set -eu
LOG=$LOG
exec > >(tee -a "\$LOG") 2>&1
echo ""
echo "## Phase 0 — Pre-flight (\$(date -u +%FT%TZ))"
hostname
df -h /
free -h
docker --version
docker ps --format "table {{.Names}}\t{{.Status}}"
if docker ps -a --format "{{.Names}}" | grep -qi hermes; then
  echo "WARNING: hermes containers already exist:"
  docker ps -a --format "{{.Names}}" | grep -i hermes
fi
if [ -d $INSTALL_DIR ] && [ -f $INSTALL_DIR/docker-compose.yml ]; then
  echo "INFO: $INSTALL_DIR already populated — install is idempotent, continuing"
fi
getent hosts $HERMES_SUBDOMAIN
echo "HTTP :80  -> \$(curl -sI -o /dev/null -w '%{http_code}' --max-time 5 http://$HERMES_SUBDOMAIN/)"
echo "HTTPS :443 -> \$(curl -sI -o /dev/null -w '%{http_code}' --max-time 10 -k https://$HERMES_SUBDOMAIN/)"
PRE

echo "==> Phase 1: discover Traefik"
TRAEFIK_INFO=$(ssh_bash <<'D'
TRAEFIK=$(docker ps --format "{{.Names}}" | grep -i traefik | head -1)
NET=$(docker inspect "$TRAEFIK" --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' | head -1)
RESOLVER=""
for c in $(docker ps --format "{{.Names}}" | grep -v -i traefik); do
  R=$(docker inspect "$c" --format '{{range $k, $v := .Config.Labels}}{{if and (eq (slice $k 0 8) "traefik.") (gt (len $k) 8)}}{{$v}}{{"\n"}}{{end}}{{end}}' 2>/dev/null | grep -E "^[a-zA-Z0-9_-]+$" | head -1) || true
  R2=$(docker inspect "$c" --format '{{range $k, $v := .Config.Labels}}{{if and (eq (slice $k 0 8) "traefik.") (gt (len $k) 8)}}{{$k}}={{$v}}{{"\n"}}{{end}}{{end}}' 2>/dev/null | grep "certresolver=" | head -1 | cut -d= -f2)
  if [ -n "$R2" ]; then RESOLVER="$R2"; break; fi
done
[ -z "$RESOLVER" ] && RESOLVER=letsencrypt   # safe default
echo "TRAEFIK_CONTAINER=$TRAEFIK"
echo "TRAEFIK_NETWORK=$NET"
echo "CERT_RESOLVER_NAME=$RESOLVER"
D
)
echo "$TRAEFIK_INFO"
TRAEFIK_NETWORK=$(echo "$TRAEFIK_INFO" | grep TRAEFIK_NETWORK | cut -d= -f2)
CERT_RESOLVER_NAME=$(echo "$TRAEFIK_INFO" | grep CERT_RESOLVER_NAME | cut -d= -f2)

echo "==> Phase 2: prepare secrets"
ssh_bash <<S
set -eu
mkdir -p $INSTALL_DIR $DATA_DIR
chmod 755 $INSTALL_DIR
chmod 700 $DATA_DIR
which htpasswd >/dev/null 2>&1 || apt-get install -y apache2-utils >/dev/null 2>&1

TRAEFIK_BASIC_PASS=\$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
RAW_HASH=\$(htpasswd -nbB "$TRAEFIK_BASIC_AUTH_USER" "\$TRAEFIK_BASIC_PASS")
HASH_ESCAPED=\$(echo "\$RAW_HASH" | sed 's/\$/\$\$/g')

cat > $CREDS <<EOF
HERMES INSTALL CREDENTIALS
==========================
WebUI URL: https://$HERMES_SUBDOMAIN
Traefik basic auth:
  Username: $TRAEFIK_BASIC_AUTH_USER
  Password: \$TRAEFIK_BASIC_PASS

OpenRouter API key:  NOT CONFIGURED
  Edit $DATA_DIR/.env and set OPENROUTER_API_KEY=sk-or-v1-... then:
  cd $INSTALL_DIR && docker compose restart

OR use Anthropic OAuth via the dashboard:
  Dashboard → Settings → Providers → Add Anthropic via Subscription / OAuth
EOF
chmod 600 $CREDS

echo "\$HASH_ESCAPED" > $INSTALL_DIR/.basic_auth_hash_escaped
chmod 600 $INSTALL_DIR/.basic_auth_hash_escaped
echo "creds written to $CREDS (not echoed)"
S

echo "==> Phase 3: render compose"
ssh_bash <<R
set -eu
HASH=\$(cat $INSTALL_DIR/.basic_auth_hash_escaped)

python3 - "\$HASH" > $INSTALL_DIR/docker-compose.yml <<PY
import sys, textwrap
hash_escaped = sys.argv[1]
print(textwrap.dedent(f'''\\
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    env_file:
      - $DATA_DIR/.env
    environment:
      - HERMES_DASHBOARD=1
      - HERMES_DASHBOARD_HOST=0.0.0.0
      - HERMES_DASHBOARD_PORT=9119
    volumes:
      - $DATA_DIR:/opt/data
    networks:
      - $TRAEFIK_NETWORK
    deploy:
      resources:
        limits:
          memory: $CONTAINER_MEMORY_LIMIT
          cpus: "$CONTAINER_CPU_LIMIT"
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:9119/ -o /dev/null || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 90s
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=$TRAEFIK_NETWORK"
      - "traefik.http.routers.hermes.rule=Host(\\\`$HERMES_SUBDOMAIN\\\`)"
      - "traefik.http.routers.hermes.entrypoints=websecure"
      - "traefik.http.routers.hermes.tls=true"
      - "traefik.http.routers.hermes.tls.certresolver=$CERT_RESOLVER_NAME"
      - "traefik.http.routers.hermes.middlewares=hermes-auth@docker"
      - "traefik.http.middlewares.hermes-auth.basicauth.users={hash_escaped}"
      - "traefik.http.services.hermes.loadbalancer.server.port=9119"
      - "traefik.http.routers.hermes.service=hermes"

networks:
  $TRAEFIK_NETWORK:
    external: true
'''))
PY

cd $INSTALL_DIR && docker compose config --quiet && echo "compose syntax OK"
R

echo "==> Phase 4: pre-populate .env"
ssh_bash <<EE
[ -f $DATA_DIR/.env ] || cat > $DATA_DIR/.env <<EOF
OPENROUTER_API_KEY=PLACEHOLDER_REPLACE_AFTER_INSTALL
EOF
chmod 600 $DATA_DIR/.env
EE

echo "==> Phase 5: docker compose up"
ssh_bash <<U
cd $INSTALL_DIR
docker compose pull
docker compose up -d
for i in \$(seq 1 36); do
  s=\$(docker inspect hermes --format '{{.State.Health.Status}}' 2>/dev/null || echo no-health)
  printf 't=%3ds %s\n' \$((i*5)) \$s
  [ "\$s" = healthy ] && exit 0
  [ "\$s" = unhealthy ] && { docker logs --tail 80 hermes; exit 1; }
  sleep 5
done
echo "TIMEOUT waiting for healthy"
docker logs --tail 80 hermes
exit 1
U

echo "==> Phase 6: smoke tests (strict — no -k)"
ssh_bash <<T
PASS=\$(awk '/^  Password:/ {print \$2; exit}' $CREDS)
echo "=== Test 1: external DNS ==="
nslookup $HERMES_SUBDOMAIN 8.8.8.8 | grep -E "Address|Name"
echo "=== Test 2: TLS chain (no -k) ==="
echo | openssl s_client -connect $HERMES_SUBDOMAIN:443 -servername $HERMES_SUBDOMAIN 2>&1 | grep -E "Verification|depth=|subject="
echo "=== Test 3: HTTPS no creds (expect 401) ==="
curl -sI --max-time 10 https://$HERMES_SUBDOMAIN/ -o /dev/null -w "%{http_code}\n"
echo "=== Test 4: HTTPS with creds (expect 200) ==="
curl -s --max-time 10 -u "$TRAEFIK_BASIC_AUTH_USER:\$PASS" https://$HERMES_SUBDOMAIN/ -o /dev/null -w "%{http_code}\n"
echo "=== Test 5: cert subject + dates ==="
echo | openssl s_client -connect $HERMES_SUBDOMAIN:443 -servername $HERMES_SUBDOMAIN 2>/dev/null | openssl x509 -noout -subject -issuer -dates
T

echo ""
echo "==> DONE"
echo "    WebUI:        https://$HERMES_SUBDOMAIN"
echo "    Credentials:  $CREDS (on VPS, chmod 600)"
echo "    Audit:        $LOG (on VPS)"
echo "    Compose:      $INSTALL_DIR/docker-compose.yml (on VPS)"
echo ""
echo "Next:"
echo "    1. Browse to the URL and authenticate with the Traefik creds"
echo "    2. Dashboard → Settings → Providers → Add Anthropic via Subscription (recommended if you have Claude Pro/Max)"
echo "    3. (Optional) Telegram, MCP, Gmail wiring — see references/follow-on-extensions.md"

# ============================================================================
# Cleanup (uncomment to wipe a deploy and start fresh)
# ============================================================================
# ssh "$SSH_ALIAS" "cd $INSTALL_DIR && docker compose down -v && rm -rf $INSTALL_DIR && rm -f $CREDS $LOG"
