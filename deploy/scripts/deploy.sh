#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
    echo "ERRO: arquivo .env não encontrado." >&2
    exit 1
fi

COMPOSE=(docker compose --env-file .env -f compose.yaml -f compose.production.yaml)

echo "Validando configuração..."
"${COMPOSE[@]}" config >/dev/null

echo "Baixando imagens..."
"${COMPOSE[@]}" pull

echo "Iniciando infraestrutura..."
"${COMPOSE[@]}" up -d postgres redis

echo "Executando migrações..."
"${COMPOSE[@]}" run --rm --no-deps app php artisan migrate --force

echo "Atualizando aplicação..."
"${COMPOSE[@]}" up -d --remove-orphans

echo "Otimizando Laravel..."
"${COMPOSE[@]}" exec -T app php artisan optimize
"${COMPOSE[@]}" exec -T app php artisan queue:restart || true

echo "Validando saúde..."
bash "$(dirname "$0")/healthcheck.sh"

echo "Deploy concluído."
