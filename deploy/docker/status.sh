#!/usr/bin/env bash
set -Eeuo pipefail
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"
load_env
compose ps
printf '\nImagens configuradas:\n'
printf '  APP:       %s\n' "$APP_IMAGE"
printf '  GATEWAY:   %s\n' "$GATEWAY_IMAGE"
printf '  CONVERTER: %s\n' "$CONVERTER_IMAGE"
