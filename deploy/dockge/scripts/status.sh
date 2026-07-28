#!/usr/bin/env bash
set -Eeuo pipefail
STACK_DIR="${STACK_DIR:-/opt/stacks/pdf2ofx}"
cd "$STACK_DIR"
docker compose --env-file .env -f compose.yaml ps
docker compose --env-file .env -f compose.yaml images
