#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
wait_for_health postgres 180
wait_for_health redis 120
wait_for_health converter-api 240
wait_for_health app 240
compose exec -T app php artisan migrate --force
compose exec -T app php artisan optimize
compose exec -T app php artisan queue:restart || true
bash "$STACK_DIR/scripts/healthcheck.sh"
