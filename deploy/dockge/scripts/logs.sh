#!/usr/bin/env bash
set -Eeuo pipefail
STACK_DIR="${STACK_DIR:-/opt/stacks/pdf2ofx}"
cd "$STACK_DIR"
SERVICE="${1:-}"
if [[ -n "$SERVICE" ]]; then
    exec docker compose --env-file .env -f compose.yaml logs -f --tail=200 "$SERVICE"
fi
exec docker compose --env-file .env -f compose.yaml logs -f --tail=100
