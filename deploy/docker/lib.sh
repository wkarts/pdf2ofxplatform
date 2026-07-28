#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PDF2OFX_ENV_FILE:-$DEPLOY_DIR/.env}"
COMPOSE_FILE="$DEPLOY_DIR/compose.yaml"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "ERRO: comando obrigatório não encontrado: $1" >&2
        exit 1
    }
}

require_env_file() {
    if [[ ! -f "$ENV_FILE" ]]; then
        echo "ERRO: arquivo $ENV_FILE não encontrado." >&2
        echo "Execute: bash $DEPLOY_DIR/install.sh --domain https://seu-dominio" >&2
        exit 1
    fi
}

load_env() {
    require_env_file
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
}

set_env_value() {
    local key="$1"
    local value="$2"
    local escaped
    escaped="${value//&/\\&}"

    if grep -qE "^${key}=" "$ENV_FILE"; then
        sed -i -E "s|^${key}=.*$|${key}=${escaped}|" "$ENV_FILE"
    else
        printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
    fi
}

validate_no_placeholders() {
    if grep -nE 'SUBSTITUIR_|GENERATE_WITH|exemplo\.com\.br' "$ENV_FILE"; then
        echo "ERRO: o arquivo .env ainda possui valores de exemplo." >&2
        exit 1
    fi
}

compose() {
    "${COMPOSE[@]}" "$@"
}
