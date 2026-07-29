#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

DOMAIN="pdf2ofx.seudominio.com.br"
VERSION="$(tr -d '[:space:]' < "$STACK_DIR/VERSION")"
NAMESPACE="wkarts"
PORT="8080"
FORCE=false

usage() {
    cat <<'EOF'
Uso:
  bash scripts/configure.sh [opções]

Opções:
  --domain HOST           domínio sem caminho (padrão: pdf2ofx.seudominio.com.br)
  --version X.Y.Z         versão das imagens
  --namespace USUARIO     namespace do GHCR (padrão: wkarts)
  --port PORTA            porta local do gateway (padrão: 8080)
  --force                 recria o .env e gera novas credenciais
  -h, --help              exibe esta ajuda
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain) DOMAIN="${2:?Informe o domínio}"; shift 2 ;;
        --version) VERSION="${2:?Informe a versão}"; shift 2 ;;
        --namespace) NAMESPACE="${2:?Informe o namespace}"; shift 2 ;;
        --port) PORT="${2:?Informe a porta}"; shift 2 ;;
        --force) FORCE=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) fail "opção desconhecida: $1" ;;
    esac
done

DOMAIN="${DOMAIN#http://}"
DOMAIN="${DOMAIN#https://}"
DOMAIN="${DOMAIN%%/*}"
[[ "$DOMAIN" =~ ^[A-Za-z0-9.-]+$ ]] || fail "domínio inválido: $DOMAIN"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]] || fail "versão inválida: $VERSION"
[[ "$NAMESPACE" =~ ^[A-Za-z0-9._-]+$ ]] || fail "namespace GHCR inválido"
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT >= 1 && PORT <= 65535 )) || fail "porta inválida: $PORT"

if [[ -f "$ENV_FILE" && "$FORCE" != true ]]; then
    echo "O arquivo $ENV_FILE já existe e foi preservado. Use --force para recriá-lo."
    exit 0
fi

need_command openssl
cp "$STACK_DIR/.env.example" "$ENV_FILE"

DB_PASSWORD="$(openssl rand -hex 24)"
REDIS_PASSWORD="$(openssl rand -hex 24)"
INTERNAL_KEY="$(openssl rand -hex 32)"
APP_KEY="base64:$(openssl rand -base64 32 | tr -d '\n')"

replace_env PDF2OFX_VERSION "$VERSION"
replace_env GHCR_NAMESPACE "$NAMESPACE"
replace_env APP_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-app:${VERSION}"
replace_env GATEWAY_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-gateway:${VERSION}"
replace_env CONVERTER_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-converter:${VERSION}"
replace_env REDIS_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-base-redis:8-alpine"
replace_env POSTGRES_IMAGE "ghcr.io/${NAMESPACE}/pdf2ofx-base-postgres:17-alpine"
replace_env APP_URL "https://${DOMAIN}"
replace_env APP_KEY "$APP_KEY"
replace_env DB_PASSWORD "$DB_PASSWORD"
replace_env REDIS_PASSWORD "$REDIS_PASSWORD"
replace_env CONVERTER_API_KEY "$INTERNAL_KEY"
replace_env PDF2OFX_API_KEY "$INTERNAL_KEY"
replace_env PDF2OFX_REDIS_URL "redis://:${REDIS_PASSWORD}@redis:6379/0"
replace_env WEB_HOST_PORT "$PORT"
replace_env PDF2OFX_HEALTH_URL "http://127.0.0.1:${PORT}/health"
chmod 600 "$ENV_FILE"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    compose config >/dev/null
fi

cat <<EOF
Configuração criada em: $ENV_FILE
Domínio: https://${DOMAIN}
Versão: ${VERSION}
Porta local: 127.0.0.1:${PORT}

Próximo comando:
  bash scripts/deploy.sh
EOF
