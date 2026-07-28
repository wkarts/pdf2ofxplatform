#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"
load_env

BACKUP_DIR="${BACKUP_DIR:-$DEPLOY_DIR/backups}"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
TARGET="$BACKUP_DIR/pdf2ofx_${STAMP}.sql.gz"
ENV_TARGET="$BACKUP_DIR/pdf2ofx_${STAMP}.env"

compose exec -T postgres \
    pg_dump -U "$DB_USERNAME" -d "$DB_DATABASE" --no-owner --no-acl \
    | gzip -9 > "$TARGET"
cp "$ENV_FILE" "$ENV_TARGET"
chmod 600 "$TARGET" "$ENV_TARGET"
sha256sum "$TARGET" "$ENV_TARGET" > "$BACKUP_DIR/pdf2ofx_${STAMP}.sha256"

find "$BACKUP_DIR" -type f -name 'pdf2ofx_*' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
printf 'Backup criado:\n  %s\n  %s\n' "$TARGET" "$ENV_TARGET"
