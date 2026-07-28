#!/usr/bin/env bash
set -Eeuo pipefail
STACK_DIR="${STACK_DIR:-/opt/stacks/pdf2ofx}"
cd "$STACK_DIR"
docker compose --env-file .env -f compose.yaml exec -T app php artisan migrate --force
docker compose --env-file .env -f compose.yaml exec -T app php artisan optimize
docker compose --env-file .env -f compose.yaml exec -T app php artisan queue:restart || true
bash scripts/healthcheck.sh
