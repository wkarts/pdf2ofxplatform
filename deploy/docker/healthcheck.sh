#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"

require_command curl
load_env
URL="${PDF2OFX_HEALTH_URL:-http://127.0.0.1:${WEB_HOST_PORT:-8080}/health}"

for attempt in $(seq 1 30); do
    if curl --fail --silent --show-error --max-time 5 "$URL" | grep -Fxq ok; then
        echo "Aplicação saudável em $URL"
        exit 0
    fi
    echo "Aguardando aplicação ($attempt/30)..."
    sleep 2
done

compose ps >&2 || true
echo "ERRO: aplicação não respondeu em $URL" >&2
exit 1
