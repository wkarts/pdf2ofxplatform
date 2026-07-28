#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=deploy/docker/lib.sh
source "$DEPLOY_DIR/lib.sh"

DOMAIN=""
VERSION="1.1.7"
NAMESPACE="wkarts"
WEB_PORT="8080"
FORCE="false"

usage() {
    cat <<'USAGE'
Uso:
  bash install.sh --domain https://pdf2ofx.exemplo.com.br [opções]

Opções:
  --domain URL       URL pública obrigatória, com https://
  --version X.Y.Z    versão das imagens (padrão: 1.1.7)
  --namespace NOME   namespace do GHCR (padrão: wkarts)
  --port PORTA       porta local para o CloudPanel (padrão: 8080)
  --force            recriar o .env existente
  -h, --help         exibir ajuda

Para pacote privado no GHCR, exporte antes:
  export GHCR_USER=wkarts
  export GHCR_TOKEN=SEU_TOKEN_COM_READ_PACKAGES
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain) DOMAIN="${2:-}"; shift 2 ;;
        --version) VERSION="${2:-}"; shift 2 ;;
        --namespace) NAMESPACE="${2:-}"; shift 2 ;;
        --port) WEB_PORT="${2:-}"; shift 2 ;;
        --force) FORCE="true"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERRO: argumento desconhecido: $1" >&2; usage; exit 1 ;;
    esac
done

[[ "$DOMAIN" =~ ^https://[^/]+/?$ ]] || {
    echo "ERRO: informe --domain com uma URL HTTPS válida." >&2
    usage
    exit 1
}
DOMAIN="${DOMAIN%/}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]] || {
    echo "ERRO: versão inválida: $VERSION" >&2
    exit 1
}
[[ "$WEB_PORT" =~ ^[0-9]+$ ]] || {
    echo "ERRO: porta inválida: $WEB_PORT" >&2
    exit 1
}

require_command docker
require_command openssl
docker compose version >/dev/null

if [[ -f "$ENV_FILE" && "$FORCE" != "true" ]]; then
    echo "ERRO: $ENV_FILE já existe. Use --force apenas se desejar recriá-lo." >&2
    exit 1
fi

cp "$DEPLOY_DIR/.env.example" "$ENV_FILE"
chmod 600 "$ENV_FILE"

DB_PASSWORD="$(openssl rand -hex 32)"
REDIS_PASSWORD="$(openssl rand -hex 32)"
INTERNAL_KEY="$(openssl rand -hex 48)"

set_env_value PDF2OFX_VERSION "$VERSION"
set_env_value GHCR_NAMESPACE "$NAMESPACE"
set_env_value APP_URL "$DOMAIN"
set_env_value WEB_HOST_PORT "$WEB_PORT"
set_env_value PDF2OFX_HEALTH_URL "http://127.0.0.1:${WEB_PORT}/health"
set_env_value DB_PASSWORD "$DB_PASSWORD"
set_env_value REDIS_PASSWORD "$REDIS_PASSWORD"
set_env_value CONVERTER_API_KEY "$INTERNAL_KEY"
set_env_value PDF2OFX_API_KEY "$INTERNAL_KEY"
set_env_value PDF2OFX_REDIS_URL "redis://:${REDIS_PASSWORD}@redis:6379/0"
set_env_value APP_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-app:${VERSION}"
set_env_value GATEWAY_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-gateway:${VERSION}"
set_env_value CONVERTER_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-converter:${VERSION}"
set_env_value REDIS_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-base-redis:8-alpine"
set_env_value POSTGRES_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-base-postgres:17-alpine"

if [[ -n "${GHCR_TOKEN:-}" ]]; then
    GHCR_USER="${GHCR_USER:-$NAMESPACE}"
    printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
fi

load_env
echo "Baixando a imagem Laravel para gerar APP_KEY..."
docker pull "$APP_IMAGE"
APP_KEY="$(docker run --rm --entrypoint php "$APP_IMAGE" artisan key:generate --show --no-ansi | tr -d '\r\n')"
[[ "$APP_KEY" == base64:* ]] || {
    echo "ERRO: não foi possível gerar uma APP_KEY válida." >&2
    exit 1
}
set_env_value APP_KEY "$APP_KEY"

validate_no_placeholders
bash "$DEPLOY_DIR/deploy.sh"

cat <<EOF2

Instalação concluída.

CloudPanel Reverse Proxy:
  http://127.0.0.1:${WEB_PORT}

URL pública:
  ${DOMAIN}

Arquivo de configuração:
  ${ENV_FILE}

Proteja e faça backup desse arquivo. Ele contém as chaves da aplicação.
EOF2
