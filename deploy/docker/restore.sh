#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! -f "$1" ]]; then
    echo "Uso: RESTORE_CONFIRM=YES bash restore.sh /caminho/backup.sql.gz" >&2
    exit 1
fi
[[ "${RESTORE_CONFIRM:-}" == "YES" ]] || {
    echo "ERRO: defina RESTORE_CONFIRM=YES para confirmar a restauração destrutiva." >&2
    exit 1
}

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"
load_env
BACKUP_FILE="$(realpath "$1")"

compose up -d --wait --wait-timeout 180 postgres
compose stop app queue scheduler converter-api converter-worker converter-cleaner gateway || true

gzip -dc "$BACKUP_FILE" | compose exec -T postgres \
    psql -v ON_ERROR_STOP=1 -U "$DB_USERNAME" -d "$DB_DATABASE"

compose up -d --remove-orphans --wait --wait-timeout 300
compose exec -T app php artisan migrate --force
compose exec -T app php artisan optimize
bash "$DEPLOY_DIR/healthcheck.sh"
echo "Restauração concluída."
