#!/usr/bin/env bash
set -Eeuo pipefail
if [[ $# -ne 1 || ! "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
    echo "Uso: bash scripts/update-version.sh X.Y.Z" >&2
    exit 1
fi
STACK_DIR="${STACK_DIR:-/opt/stacks/pdf2ofx}"
VERSION="$1"
cd "$STACK_DIR"
cp -a .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
sed -i -E "s#^(PDF2OFX_VERSION=).*$#\1${VERSION}#" .env
sed -i -E "s#^(APP_IMAGE=ghcr.io/[^:]+/pdf2ofx-app:).*$#\1${VERSION}#" .env
sed -i -E "s#^(GATEWAY_IMAGE=ghcr.io/[^:]+/pdf2ofx-gateway:).*$#\1${VERSION}#" .env
sed -i -E "s#^(CONVERTER_IMAGE=ghcr.io/[^:]+/pdf2ofx-converter:).*$#\1${VERSION}#" .env
docker compose --env-file .env -f compose.yaml config >/dev/null
docker compose --env-file .env -f compose.yaml pull
docker compose --env-file .env -f compose.yaml up -d --remove-orphans
bash scripts/post-deploy.sh
echo "Stack atualizada para ${VERSION}."
