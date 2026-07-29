#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"
[[ $# -eq 1 ]] || fail "uso: bash scripts/restore.sh backups/postgres_AAAAMMDD_HHMMSS.sql.gz"
FILE="$1"
[[ -f "$FILE" ]] || fail "backup não encontrado: $FILE"
DB_USER="$(read_env DB_USERNAME)"
DB_NAME="$(read_env DB_DATABASE)"
echo "ATENÇÃO: o banco $DB_NAME será recriado a partir de $FILE."
read -r -p 'Digite RESTAURAR para continuar: ' CONFIRM
[[ "$CONFIRM" == RESTAURAR ]] || fail "restauração cancelada"
compose stop app queue scheduler converter-api converter-worker converter-cleaner
compose exec -T postgres dropdb -U "$DB_USER" --if-exists "$DB_NAME"
compose exec -T postgres createdb -U "$DB_USER" "$DB_NAME"
gzip -dc "$FILE" | compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME"
compose up -d
bash "$STACK_DIR/scripts/post-deploy.sh"
