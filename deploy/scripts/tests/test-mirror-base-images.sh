#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

mkdir -p "$TEMP_DIR/bin" "$TEMP_DIR/state"

cat > "$TEMP_DIR/bin/docker" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail

echo "$*" >> "$MOCK_LOG"

if [[ "$1 $2" == "manifest inspect" ]]; then
    image="$3"

    if [[ "$image" == *"pdf2ofx-base-redis:8-alpine"* ]]; then
        [[ -f "$MOCK_STATE/redis-pushed" ]]
        exit $?
    fi

    exit 0
fi

if [[ "$1" == "push" && "$2" == *"pdf2ofx-base-redis:8-alpine"* ]]; then
    count_file="$MOCK_STATE/redis-push-count"
    count=0
    [[ -f "$count_file" ]] && count="$(cat "$count_file")"
    count=$((count + 1))
    printf '%s' "$count" > "$count_file"

    if (( count == 1 )); then
        echo "429 Too Many Requests" >&2
        exit 1
    fi

    touch "$MOCK_STATE/redis-pushed"
    exit 0
fi

exit 0
MOCK
chmod +x "$TEMP_DIR/bin/docker"

export PATH="$TEMP_DIR/bin:$PATH"
export MOCK_LOG="$TEMP_DIR/docker.log"
export MOCK_STATE="$TEMP_DIR/state"
export GHCR_OWNER="wkarts"
export FORCE_MIRROR="false"
export MAX_ATTEMPTS="3"
export INITIAL_DELAY_SECONDS="0"
export BETWEEN_IMAGES_DELAY_SECONDS="0"

"$ROOT_DIR/deploy/scripts/mirror-base-images.sh"

pull_count="$(grep -c '^pull --platform linux/amd64 docker.io/library/redis:8-alpine$' "$MOCK_LOG")"
push_count="$(grep -c '^push ghcr.io/wkarts/pdf2ofx-base-redis:8-alpine$' "$MOCK_LOG")"
tag_count="$(grep -c '^tag docker.io/library/redis:8-alpine ghcr.io/wkarts/pdf2ofx-base-redis:8-alpine$' "$MOCK_LOG")"

[[ "$pull_count" == "1" ]]
[[ "$push_count" == "2" ]]
[[ "$tag_count" == "1" ]]
[[ "$(cat "$TEMP_DIR/state/redis-push-count")" == "2" ]]

if grep -q '^pull .*php:8.4-fpm-alpine' "$MOCK_LOG"; then
    echo "ERRO: uma imagem já existente foi republicada." >&2
    exit 1
fi

echo "Teste do espelhamento sequencial e retry aprovado."
