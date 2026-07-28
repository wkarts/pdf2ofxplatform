#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TEMP_DIR="$(mktemp -d)"
MOCK_DOCKER_LOG="$TEMP_DIR/docker.log"

run_as_root() {
    if (( EUID == 0 )); then
        "$@"
        return
    fi

    if ! command -v sudo >/dev/null 2>&1; then
        echo "ERRO: o teste requer root ou sudo para reproduzir a instalação da VPS." >&2
        exit 1
    fi

    sudo -E "$@"
}

cleanup() {
    run_as_root rm -rf "$TEMP_DIR" >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "$TEMP_DIR/bin"
: > "$MOCK_DOCKER_LOG"
chmod 0666 "$MOCK_DOCKER_LOG"

cat > "$TEMP_DIR/bin/docker" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail

printf '%s\n' "$*" >> "$MOCK_DOCKER_LOG"
exit 0
MOCK
chmod 0755 "$TEMP_DIR/bin/docker"

# O PATH é definido depois do sudo para impedir que o secure_path substitua
# o Docker simulado pelo Docker real do runner.
run_as_root env \
    "PATH=$TEMP_DIR/bin:$PATH" \
    "MOCK_DOCKER_LOG=$MOCK_DOCKER_LOG" \
    bash "$ROOT_DIR/deploy/dockge/install-vps.sh" \
        --domain https://pdf2ofx.teste.local \
        --version 1.1.9 \
        --namespace wkarts \
        --app-port 18080 \
        --dockge-port 15001 \
        --dockge-dir "$TEMP_DIR/dockge" \
        --stacks-dir "$TEMP_DIR/stacks" \
        --stack-name pdf2ofx-test \
        --no-start \
        --skip-docker-install >/dev/null

STACK_DIR="$TEMP_DIR/stacks/pdf2ofx-test"
run_as_root test -f "$TEMP_DIR/dockge/compose.yaml"
run_as_root test -f "$STACK_DIR/compose.yaml"
run_as_root test -f "$STACK_DIR/.env"

permissions="$(run_as_root stat -c '%a' "$STACK_DIR/.env")"
[[ "$permissions" == "600" ]]

run_as_root grep -Fq 'APP_URL=https://pdf2ofx.teste.local' "$STACK_DIR/.env"
run_as_root grep -Fq 'APP_IMAGE=ghcr.io/wkarts/pdf2ofx-app:1.1.9' "$STACK_DIR/.env"
run_as_root grep -Fq 'WEB_HOST_PORT=18080' "$STACK_DIR/.env"
run_as_root grep -Fq 'DOCKGE_HOST_PORT=15001' "$TEMP_DIR/dockge/.env"

grep -Fq 'compose version' "$MOCK_DOCKER_LOG"
grep -Fq 'compose --env-file .env -f compose.yaml config' "$MOCK_DOCKER_LOG"
grep -Fq 'compose --env-file .env -f compose.yaml pull' "$MOCK_DOCKER_LOG"
grep -Fq 'compose --env-file .env -f compose.yaml up -d' "$MOCK_DOCKER_LOG"

# A validação deve usar somente o binário simulado. Se o log estiver vazio,
# significa que o sudo descartou o PATH e o teste deixou de ser isolado.
[[ -s "$MOCK_DOCKER_LOG" ]]

echo "Instalador Dockge validado com Docker simulado, sem acesso ao daemon real."
