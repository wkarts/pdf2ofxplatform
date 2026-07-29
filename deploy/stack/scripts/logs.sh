#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
if [[ $# -gt 0 ]]; then
    compose logs --tail=300 -f "$@"
else
    compose logs --tail=300 -f
fi
