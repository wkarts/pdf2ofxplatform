#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT
cp -a "$ROOT_DIR/." "$TEMP_DIR/stack/"
mkdir -p "$TEMP_DIR/bin"
cat > "$TEMP_DIR/bin/docker" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "${1:-} ${2:-}" == "compose version" ]]; then exit 0; fi
if [[ "${1:-}" == "info" ]]; then exit 0; fi
if [[ "${1:-}" == "compose" && "$*" == *" config"* ]]; then exit 0; fi
exit 0
MOCK
chmod +x "$TEMP_DIR/bin/docker"
PATH="$TEMP_DIR/bin:$PATH" STACK_DIR="$TEMP_DIR/stack" \
  bash "$TEMP_DIR/stack/scripts/configure.sh" \
    --domain pdf2ofx.seudominio.com.br \
    --version 1.2.0 \
    --namespace wkarts \
    --port 8080
ENV_FILE="$TEMP_DIR/stack/.env"
[[ "$(stat -c '%a' "$ENV_FILE")" == "600" ]]
grep -Fqx 'APP_URL=https://pdf2ofx.seudominio.com.br' "$ENV_FILE"
grep -Fqx 'APP_IMAGE=ghcr.io/wkarts/pdf2ofx-app:1.2.0' "$ENV_FILE"
grep -Eq '^APP_KEY=base64:.+' "$ENV_FILE"
! grep -Eq 'SUBSTITUIR_' "$ENV_FILE"
PATH="$TEMP_DIR/bin:$PATH" STACK_DIR="$TEMP_DIR/stack" bash "$TEMP_DIR/stack/scripts/preflight.sh"
echo "Teste da distribuição de stack existente aprovado."
