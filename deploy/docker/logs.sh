#!/usr/bin/env bash
set -Eeuo pipefail
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"
load_env
compose logs --tail="${LOG_TAIL:-300}" -f "$@"
