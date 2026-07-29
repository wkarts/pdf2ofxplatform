#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

need_command docker
need_command curl
need_command openssl

docker info >/dev/null 2>&1 || fail "o daemon Docker não está acessível"
docker compose version >/dev/null 2>&1 || fail "Docker Compose V2 não está disponível"
[[ -f "$COMPOSE_FILE" ]] || fail "compose.yaml não encontrado em $STACK_DIR"
[[ -f "$ENV_FILE" ]] || fail ".env não encontrado; execute bash scripts/configure.sh"

compose config >/dev/null

echo "Pré-validação concluída. Docker, Compose, .env e stack estão disponíveis."
