#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
[[ $# -eq 1 ]] || fail "uso: bash scripts/update.sh X.Y.Z"
VERSION="$1"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]] || fail "versão inválida: $VERSION"
[[ -f "$ENV_FILE" ]] || fail ".env não encontrado"
BACKUP="$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp -a "$ENV_FILE" "$BACKUP"
NAMESPACE="$(read_env GHCR_NAMESPACE)"
NAMESPACE="${NAMESPACE:-wkarts}"
replace_env PDF2OFX_VERSION "$VERSION"
replace_env APP_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-app:${VERSION}"
replace_env GATEWAY_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-gateway:${VERSION}"
replace_env CONVERTER_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-converter:${VERSION}"
if ! bash "$STACK_DIR/scripts/deploy.sh"; then
    cp -a "$BACKUP" "$ENV_FILE"
    compose up -d --remove-orphans || true
    fail "atualização falhou; o .env anterior foi restaurado"
fi
echo "Stack atualizada para $VERSION. Backup do ambiente: $BACKUP"
