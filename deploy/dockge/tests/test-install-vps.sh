#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT
mkdir -p "$TEMP_DIR/bin"

cat > "$TEMP_DIR/bin/docker" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$MOCK_DOCKER_LOG"
exit 0
MOCK
chmod +x "$TEMP_DIR/bin/docker"

export MOCK_DOCKER_LOG="$TEMP_DIR/docker.log"
export PATH="$TEMP_DIR/bin:$PATH"

bash "$ROOT_DIR/deploy/dockge/install-vps.sh" \
    --domain https://pdf2ofx.teste.local \
    --version 1.1.7 \
    --namespace wkarts \
    --app-port 18080 \
    --dockge-port 15001 \
    --dockge-dir "$TEMP_DIR/dockge" \
    --stacks-dir "$TEMP_DIR/stacks" \
    --stack-name pdf2ofx-test \
    --no-start \
    --skip-docker-install >/dev/null

STACK_DIR="$TEMP_DIR/stacks/pdf2ofx-test"
[[ -f "$TEMP_DIR/dockge/compose.yaml" ]]
[[ -f "$STACK_DIR/compose.yaml" ]]
[[ -f "$STACK_DIR/.env" ]]
[[ "$(stat -c '%a' "$STACK_DIR/.env")" == "600" ]]
grep -Fq 'APP_URL=https://pdf2ofx.teste.local' "$STACK_DIR/.env"
grep -Fq 'APP_IMAGE=ghcr.io/wkarts/pdf2ofx-app:1.1.7' "$STACK_DIR/.env"
grep -Fq 'WEB_HOST_PORT=18080' "$STACK_DIR/.env"
grep -Fq 'DOCKGE_HOST_PORT=15001' "$TEMP_DIR/dockge/.env"
grep -Fq 'compose --env-file .env -f compose.yaml config' "$MOCK_DOCKER_LOG"
grep -Fq 'compose --env-file .env -f compose.yaml pull' "$MOCK_DOCKER_LOG"
grep -Fq 'compose --env-file .env -f compose.yaml up -d' "$MOCK_DOCKER_LOG"

echo "Instalador Dockge validado com Docker simulado."
