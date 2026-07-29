#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
bash "$STACK_DIR/scripts/preflight.sh"
cd "$STACK_DIR"
compose pull
compose up -d --remove-orphans
bash "$STACK_DIR/scripts/post-deploy.sh"
compose ps
echo "Stack PDF2OFX implantada e pronta para gerenciamento no Dockge."
