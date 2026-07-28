#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT_DIR/.env"
    set +a
fi

URL="${PDF2OFX_HEALTH_URL:-http://127.0.0.1:${WEB_HOST_PORT:-8080}/health}"

for attempt in {1..30}; do
    if curl --fail --silent --show-error --max-time 5 "$URL" >/dev/null; then
        echo "Aplicação saudável em $URL"
        exit 0
    fi
    sleep 2
done

echo "ERRO: aplicação não respondeu em $URL" >&2
exit 1
