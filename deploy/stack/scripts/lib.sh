#!/usr/bin/env bash
set -Eeuo pipefail

STACK_DIR="${STACK_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-$STACK_DIR/compose.yaml}"
ENV_FILE="${ENV_FILE:-$STACK_DIR/.env}"

fail() {
    echo "ERRO: $*" >&2
    exit 1
}

need_command() {
    command -v "$1" >/dev/null 2>&1 || fail "comando obrigatório não encontrado: $1"
}

compose() {
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

read_env() {
    local key="$1"
    awk -F= -v key="$key" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' "$ENV_FILE"
}

replace_env() {
    local key="$1" value="$2" escaped
    escaped="$(printf '%s' "$value" | sed -e 's/[\\&|]/\\&/g')"
    if grep -q "^${key}=" "$ENV_FILE"; then
        sed -i -E "s|^${key}=.*$|${key}=${escaped}|" "$ENV_FILE"
    else
        printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
    fi
}

wait_for_health() {
    local service="$1" timeout="${2:-180}" elapsed=0 container status
    container="$(compose ps -q "$service")"
    [[ -n "$container" ]] || fail "container do serviço $service não foi criado"
    while (( elapsed < timeout )); do
        status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container" 2>/dev/null || true)"
        case "$status" in
            healthy|running) return 0 ;;
            unhealthy|exited|dead) compose logs --tail=120 "$service" >&2 || true; fail "serviço $service entrou no estado $status" ;;
        esac
        sleep 3
        elapsed=$((elapsed + 3))
    done
    compose logs --tail=120 "$service" >&2 || true
    fail "tempo excedido aguardando o serviço $service"
}
