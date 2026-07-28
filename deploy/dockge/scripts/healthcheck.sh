#!/usr/bin/env bash
set -Eeuo pipefail
STACK_DIR="${STACK_DIR:-/opt/stacks/pdf2ofx}"
cd "$STACK_DIR"
set -a
# shellcheck disable=SC1091
source .env
set +a
URL="${PDF2OFX_HEALTH_URL:-http://127.0.0.1:${WEB_HOST_PORT:-8080}/health}"
for attempt in $(seq 1 30); do
    if curl --fail --silent --show-error --max-time 10 "$URL" >/dev/null; then
        echo "PDF2OFX saudável em $URL"
        exit 0
    fi
    echo "Aguardando aplicação ($attempt/30)..."
    sleep 5
done
echo "ERRO: aplicação não respondeu em $URL" >&2
docker compose --env-file .env -f compose.yaml ps >&2 || true
exit 1
