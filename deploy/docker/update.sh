#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
    echo "Uso: bash update.sh X.Y.Z" >&2
    exit 1
fi

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"
load_env

VERSION="$1"
cp "$ENV_FILE" "$ENV_FILE.before-${VERSION}-$(date +%Y%m%d_%H%M%S)"
set_env_value PDF2OFX_VERSION "$VERSION"
set_env_value APP_IMAGE "ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-app:${VERSION}"
set_env_value GATEWAY_IMAGE "ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-gateway:${VERSION}"
set_env_value CONVERTER_IMAGE "ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-converter:${VERSION}"

bash "$DEPLOY_DIR/deploy.sh"
