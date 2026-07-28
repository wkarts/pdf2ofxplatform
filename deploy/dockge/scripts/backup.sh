#!/usr/bin/env bash
set -Eeuo pipefail
STACK_DIR="${STACK_DIR:-/opt/stacks/pdf2ofx}"
cd "$STACK_DIR"
mkdir -p backups
chmod 700 backups
set -a
# shellcheck disable=SC1091
source .env
set +a
STAMP="$(date +%Y%m%d_%H%M%S)"
BASE="backups/pdf2ofx_${STAMP}"
docker compose --env-file .env -f compose.yaml exec -T postgres \
    pg_dump -U "$DB_USERNAME" -d "$DB_DATABASE" | gzip -9 > "${BASE}.sql.gz"
cp -a .env "${BASE}.env"
chmod 600 "${BASE}.env"
sha256sum "${BASE}.sql.gz" "${BASE}.env" > "${BASE}.sha256"
find backups -type f -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
printf 'Backup criado:\n%s\n%s\n' "${BASE}.sql.gz" "${BASE}.env"
