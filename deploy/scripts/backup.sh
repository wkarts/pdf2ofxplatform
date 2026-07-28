#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
source .env

BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
TARGET="$BACKUP_DIR/pdf2ofx_${STAMP}.sql.gz"

docker compose --env-file .env exec -T postgres \
    pg_dump -U "$DB_USERNAME" -d "$DB_DATABASE" --no-owner --no-acl \
    | gzip -9 > "$TARGET"

find "$BACKUP_DIR" -type f -name 'pdf2ofx_*.sql.gz' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete

echo "$TARGET"
