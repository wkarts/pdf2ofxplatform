#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
[[ -f "$ENV_FILE" ]] || fail ".env não encontrado"
URL="$(read_env PDF2OFX_HEALTH_URL)"
URL="${URL:-http://127.0.0.1:8080/health}"
for attempt in {1..30}; do
    if response="$(curl --fail --silent --show-error --max-time 10 "$URL" 2>/dev/null)"; then
        [[ "$response" == "ok" ]] || echo "Resposta do health check: $response"
        echo "Aplicação saudável em $URL"
        exit 0
    fi
    sleep 3
done
compose ps >&2 || true
compose logs --tail=100 gateway app converter-api >&2 || true
fail "health check não respondeu em $URL"
