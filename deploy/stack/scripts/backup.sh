#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
[[ -f "$ENV_FILE" ]] || fail ".env não encontrado"
mkdir -p "$STACK_DIR/backups"
STAMP="$(date +%Y%m%d_%H%M%S)"
DB_USER="$(read_env DB_USERNAME)"
DB_NAME="$(read_env DB_DATABASE)"
compose exec -T postgres pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip -9 > "$STACK_DIR/backups/postgres_${STAMP}.sql.gz"
cp -a "$ENV_FILE" "$STACK_DIR/backups/env_${STAMP}.backup"
chmod 600 "$STACK_DIR/backups/env_${STAMP}.backup"
RETENTION="$(read_env BACKUP_RETENTION_DAYS)"
RETENTION="${RETENTION:-14}"
find "$STACK_DIR/backups" -type f -mtime "+$RETENTION" -delete
printf 'Backup concluído:\n  %s\n' "$STACK_DIR/backups/postgres_${STAMP}.sql.gz"
