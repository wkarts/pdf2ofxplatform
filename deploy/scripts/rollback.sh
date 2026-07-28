#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
    echo "Uso: $0 <versão-sem-v>" >&2
    exit 1
fi

VERSION="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
source .env

export APP_IMAGE="ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-app:${VERSION}"
export GATEWAY_IMAGE="ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-gateway:${VERSION}"
export CONVERTER_IMAGE="ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-converter:${VERSION}"

docker compose --env-file .env -f compose.yaml -f compose.production.yaml pull
docker compose --env-file .env -f compose.yaml -f compose.production.yaml up -d --remove-orphans
./deploy/scripts/healthcheck.sh
