#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"

require_command docker
require_command curl
load_env
validate_no_placeholders
docker compose version >/dev/null

cd "$DEPLOY_DIR"
echo "Validando Docker Compose..."
compose config >/dev/null

echo "Baixando imagens..."
compose pull

echo "Inicializando PostgreSQL, Redis e API de conversão..."
compose up -d --wait --wait-timeout 240 postgres redis converter-api

echo "Executando migrações Laravel..."
compose run --rm --no-deps app php artisan migrate --force

echo "Iniciando todos os serviços..."
compose up -d --remove-orphans --wait --wait-timeout 300

echo "Otimizando Laravel e reiniciando filas..."
compose exec -T app php artisan optimize
compose exec -T app php artisan queue:restart || true

bash "$DEPLOY_DIR/healthcheck.sh"
echo "Deploy concluído com sucesso."
