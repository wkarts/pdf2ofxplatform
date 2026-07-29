#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
[[ $# -eq 1 ]] || fail "uso: bash scripts/rollback.sh X.Y.Z"
bash "$STACK_DIR/scripts/update.sh" "$1"
