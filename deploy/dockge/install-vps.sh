#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACKS_DIR="/opt/stacks"
STACK_NAME="pdf2ofx"
DOCKGE_DIR="/opt/dockge"
DOCKGE_PORT="5001"
APP_PORT="8080"
APP_VERSION="1.1.8"
GHCR_NAMESPACE="wkarts"
APP_URL="https://pdf2ofx.codisplan.com.br"
START_STACK="true"
FORCE_ENV="false"
INSTALL_DOCKER="true"

usage() {
    cat <<'USAGE'
Uso:
  sudo -E bash install-vps.sh [opções]

Opções:
  --domain URL            URL pública da aplicação
  --version X.Y.Z         versão das imagens PDF2OFX
  --namespace NOME        namespace GHCR (padrão: wkarts)
  --app-port PORTA        porta local do gateway (padrão: 8080)
  --dockge-port PORTA     porta local do Dockge (padrão: 5001)
  --dockge-dir CAMINHO    diretório de dados do Dockge (padrão: /opt/dockge)
  --stacks-dir CAMINHO    diretório de stacks do Dockge (padrão: /opt/stacks)
  --stack-name NOME       nome da stack (padrão: pdf2ofx)
  --no-start              prepara os arquivos sem iniciar a aplicação
  --force-env             recria o .env da stack e gera novas credenciais
  --skip-docker-install   não instala Docker automaticamente quando ausente
  -h, --help              mostra esta ajuda

Autenticação opcional no GHCR:
  GHCR_USER=wkarts GHCR_TOKEN=... sudo -E bash install-vps.sh
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain) APP_URL="$2"; shift 2 ;;
        --version) APP_VERSION="$2"; shift 2 ;;
        --namespace) GHCR_NAMESPACE="$2"; shift 2 ;;
        --app-port) APP_PORT="$2"; shift 2 ;;
        --dockge-port) DOCKGE_PORT="$2"; shift 2 ;;
        --dockge-dir) DOCKGE_DIR="$2"; shift 2 ;;
        --stacks-dir) STACKS_DIR="$2"; shift 2 ;;
        --stack-name) STACK_NAME="$2"; shift 2 ;;
        --no-start) START_STACK="false"; shift ;;
        --force-env) FORCE_ENV="true"; shift ;;
        --skip-docker-install) INSTALL_DOCKER="false"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Opção desconhecida: $1" >&2; usage >&2; exit 1 ;;
    esac
done

if (( EUID != 0 )); then
    if command -v sudo >/dev/null 2>&1; then
        sudo_args=(
            --domain "$APP_URL"
            --version "$APP_VERSION"
            --namespace "$GHCR_NAMESPACE"
            --app-port "$APP_PORT"
            --dockge-port "$DOCKGE_PORT"
            --dockge-dir "$DOCKGE_DIR"
            --stacks-dir "$STACKS_DIR"
            --stack-name "$STACK_NAME"
        )
        [[ "$START_STACK" == "false" ]] && sudo_args+=(--no-start)
        [[ "$FORCE_ENV" == "true" ]] && sudo_args+=(--force-env)
        [[ "$INSTALL_DOCKER" == "false" ]] && sudo_args+=(--skip-docker-install)
        exec sudo -E bash "$0" "${sudo_args[@]}"
    fi
    echo "ERRO: execute como root ou com sudo." >&2
    exit 1
fi

[[ "$APP_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]] || {
    echo "ERRO: versão inválida: $APP_VERSION" >&2
    exit 1
}
[[ "$APP_PORT" =~ ^[0-9]+$ && "$DOCKGE_PORT" =~ ^[0-9]+$ ]] || {
    echo "ERRO: portas inválidas." >&2
    exit 1
}
[[ "$STACK_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] || {
    echo "ERRO: nome de stack inválido." >&2
    exit 1
}

install_docker_debian() {
    if [[ "$INSTALL_DOCKER" != "true" ]]; then
        echo "ERRO: Docker não encontrado e instalação automática desativada." >&2
        exit 1
    fi
    [[ -r /etc/os-release ]] || { echo "ERRO: distribuição não identificada." >&2; exit 1; }
    # shellcheck disable=SC1091
    source /etc/os-release
    case "${ID:-}" in
        debian|ubuntu) ;;
        *) echo "ERRO: instalação automática suportada somente em Debian/Ubuntu." >&2; exit 1 ;;
    esac
    apt-get update
    apt-get install -y ca-certificates curl gnupg openssl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL "https://download.docker.com/linux/${ID}/gpg" -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    ARCH="$(dpkg --print-architecture)"
    CODENAME="${VERSION_CODENAME:-${UBUNTU_CODENAME:-}}"
    [[ -n "$CODENAME" ]] || { echo "ERRO: codinome da distribuição não encontrado." >&2; exit 1; }
    cat > /etc/apt/sources.list.d/docker.sources <<SOURCES
Types: deb
URIs: https://download.docker.com/linux/${ID}
Suites: ${CODENAME}
Components: stable
Architectures: ${ARCH}
Signed-By: /etc/apt/keyrings/docker.asc
SOURCES
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable --now docker
}

if ! command -v docker >/dev/null 2>&1; then
    install_docker_debian
fi
docker compose version >/dev/null
command -v openssl >/dev/null 2>&1 || {
    apt-get update && apt-get install -y openssl
}
command -v curl >/dev/null 2>&1 || {
    apt-get update && apt-get install -y curl
}

STACK_DIR="${STACKS_DIR}/${STACK_NAME}"
mkdir -p "$DOCKGE_DIR/data" "$STACK_DIR/scripts" "$STACK_DIR/backups" "$STACKS_DIR"
chmod 700 "$STACK_DIR/backups"

install -m 0644 "$SOURCE_DIR/dockge/compose.yaml" "$DOCKGE_DIR/compose.yaml"
cat > "$DOCKGE_DIR/.env" <<ENV
DOCKGE_IMAGE=louislam/dockge:1
DOCKGE_HOST_PORT=${DOCKGE_PORT}
DOCKGE_STACKS_DIR=${STACKS_DIR}
ENV
chmod 600 "$DOCKGE_DIR/.env"

install -m 0644 "$SOURCE_DIR/pdf2ofx/compose.yaml" "$STACK_DIR/compose.yaml"
install -m 0755 "$SOURCE_DIR/scripts/healthcheck.sh" "$STACK_DIR/scripts/healthcheck.sh"
install -m 0755 "$SOURCE_DIR/scripts/post-deploy.sh" "$STACK_DIR/scripts/post-deploy.sh"
install -m 0755 "$SOURCE_DIR/scripts/update-version.sh" "$STACK_DIR/scripts/update-version.sh"
install -m 0755 "$SOURCE_DIR/scripts/backup.sh" "$STACK_DIR/scripts/backup.sh"
install -m 0755 "$SOURCE_DIR/scripts/logs.sh" "$STACK_DIR/scripts/logs.sh"
install -m 0755 "$SOURCE_DIR/scripts/status.sh" "$STACK_DIR/scripts/status.sh"

if [[ ! -f "$STACK_DIR/.env" || "$FORCE_ENV" == "true" ]]; then
    if [[ -f "$STACK_DIR/.env" ]]; then
        cp -a "$STACK_DIR/.env" "$STACK_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    DB_PASSWORD="$(openssl rand -hex 32)"
    REDIS_PASSWORD="$(openssl rand -hex 32)"
    INTERNAL_KEY="$(openssl rand -hex 48)"
    APP_KEY="base64:$(openssl rand -base64 32 | tr -d '\n')"
    cat > "$STACK_DIR/.env" <<ENV
COMPOSE_PROJECT_NAME=${STACK_NAME}
PDF2OFX_VERSION=${APP_VERSION}
GHCR_NAMESPACE=${GHCR_NAMESPACE}

APP_IMAGE=ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-app:${APP_VERSION}
GATEWAY_IMAGE=ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-gateway:${APP_VERSION}
CONVERTER_IMAGE=ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-converter:${APP_VERSION}
REDIS_IMAGE=ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-base-redis:8-alpine
POSTGRES_IMAGE=ghcr.io/${GHCR_NAMESPACE}/pdf2ofx-base-postgres:17-alpine

APP_NAME=PDF2OFX
APP_ENV=production
APP_KEY=${APP_KEY}
APP_DEBUG=false
APP_URL=${APP_URL}
APP_TIMEZONE=America/Sao_Paulo
APP_LOCALE=pt_BR
APP_FALLBACK_LOCALE=pt_BR
LOG_CHANNEL=stack
LOG_LEVEL=warning

DB_CONNECTION=pgsql
DB_HOST=postgres
DB_PORT=5432
DB_DATABASE=pdf2ofx
DB_USERNAME=pdf2ofx
DB_PASSWORD=${DB_PASSWORD}

CACHE_STORE=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis
REDIS_CLIENT=phpredis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}

CONVERTER_BASE_URL=http://converter-api:8000
CONVERTER_API_KEY=${INTERNAL_KEY}
CONVERTER_REQUEST_TIMEOUT=60
CONVERTER_DOWNLOAD_TIMEOUT=300
MAX_UPLOAD_KB=51200

PDF2OFX_ENV=production
PDF2OFX_API_KEY=${INTERNAL_KEY}
PDF2OFX_REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
PDF2OFX_DATA_DIR=/data/jobs
PDF2OFX_MAX_FILE_SIZE=52428800
PDF2OFX_JOB_TTL_HOURS=24
PDF2OFX_OCR_ENABLED=true
PDF2OFX_OCR_LANGUAGE=por
PDF2OFX_MAX_PAGES=200
PDF2OFX_OCR_DPI=180
PDF2OFX_OCR_PSM=6
PDF2OFX_OCR_WORKERS=1
PDF2OFX_OCR_PAGE_TIMEOUT_SECONDS=180
PDF2OFX_CELERY_EAGER=false
PDF2OFX_CORS_ORIGINS=[]

WEB_HOST_PORT=${APP_PORT}
PDF2OFX_HEALTH_URL=http://127.0.0.1:${APP_PORT}/health
CONVERTER_WORKER_CONCURRENCY=2
CONVERTER_API_TMPFS_SIZE=1024m
CONVERTER_WORKER_TMPFS_SIZE=2048m
POSTGRES_SHM_SIZE=256m
BACKUP_RETENTION_DAYS=14
ENV
    chmod 600 "$STACK_DIR/.env"
else
    echo "Arquivo $STACK_DIR/.env preservado. Use --force-env para recriá-lo."
fi

if [[ -n "${GHCR_TOKEN:-}" ]]; then
    GHCR_LOGIN_USER="${GHCR_USER:-$GHCR_NAMESPACE}"
    printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_LOGIN_USER" --password-stdin
fi

(
    cd "$DOCKGE_DIR"
    docker compose --env-file .env -f compose.yaml config >/dev/null
    docker compose --env-file .env -f compose.yaml pull
    docker compose --env-file .env -f compose.yaml up -d
)

if [[ "$START_STACK" == "true" ]]; then
    (
        cd "$STACK_DIR"
        docker compose --env-file .env -f compose.yaml config >/dev/null
        docker compose --env-file .env -f compose.yaml pull
        docker compose --env-file .env -f compose.yaml up -d postgres redis converter-api app
        for attempt in $(seq 1 30); do
            if docker compose --env-file .env -f compose.yaml exec -T app php-fpm -t >/dev/null 2>&1; then
                break
            fi
            if [[ "$attempt" == "30" ]]; then
                docker compose --env-file .env -f compose.yaml ps >&2 || true
                echo "ERRO: serviço app não ficou pronto." >&2
                exit 1
            fi
            sleep 4
        done
        docker compose --env-file .env -f compose.yaml exec -T app php artisan migrate --force
        docker compose --env-file .env -f compose.yaml exec -T app php artisan optimize
        docker compose --env-file .env -f compose.yaml up -d --remove-orphans
        bash scripts/healthcheck.sh
    )
fi

cat <<SUMMARY

Instalação preparada com sucesso.

Dockge local:       http://127.0.0.1:${DOCKGE_PORT}
Aplicação local:    http://127.0.0.1:${APP_PORT}
Stack no servidor: ${STACK_DIR}

CloudPanel — aplicação:
  Reverse Proxy -> http://127.0.0.1:${APP_PORT}

CloudPanel — Dockge (opcional, proteja o subdomínio):
  Reverse Proxy -> http://127.0.0.1:${DOCKGE_PORT}

No Dockge, use "Scan Stacks Folder" caso a stack ${STACK_NAME} não apareça automaticamente.
SUMMARY
