#!/usr/bin/env bash
set -Eeuo pipefail

: "${GHCR_OWNER:?A variável GHCR_OWNER é obrigatória.}"

FORCE_MIRROR="${FORCE_MIRROR:-false}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-6}"
INITIAL_DELAY_SECONDS="${INITIAL_DELAY_SECONDS:-10}"
BETWEEN_IMAGES_DELAY_SECONDS="${BETWEEN_IMAGES_DELAY_SECONDS:-8}"

if [[ ! "$MAX_ATTEMPTS" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERRO: MAX_ATTEMPTS deve ser um inteiro positivo." >&2
    exit 1
fi

if [[ ! "$INITIAL_DELAY_SECONDS" =~ ^[0-9]+$ ]]; then
    echo "ERRO: INITIAL_DELAY_SECONDS deve ser um inteiro não negativo." >&2
    exit 1
fi

if [[ ! "$BETWEEN_IMAGES_DELAY_SECONDS" =~ ^[0-9]+$ ]]; then
    echo "ERRO: BETWEEN_IMAGES_DELAY_SECONDS deve ser um inteiro não negativo." >&2
    exit 1
fi

retry() {
    local description="$1"
    shift

    local attempt=1
    local delay="$INITIAL_DELAY_SECONDS"

    until "$@"; do
        if (( attempt >= MAX_ATTEMPTS )); then
            echo "ERRO: ${description} falhou após ${MAX_ATTEMPTS} tentativas." >&2
            return 1
        fi

        echo "AVISO: ${description} falhou na tentativa ${attempt}/${MAX_ATTEMPTS}." >&2
        echo "Nova tentativa em ${delay}s..." >&2

        if (( delay > 0 )); then
            sleep "$delay"
        fi

        attempt=$((attempt + 1))
        delay=$((delay * 2))
    done
}

image_exists() {
    local image="$1"
    docker manifest inspect "$image" >/dev/null 2>&1
}

mirror_image() {
    local source="$1"
    local target="$2"

    if [[ "$FORCE_MIRROR" != "true" ]] && image_exists "$target"; then
        echo "Imagem-base já existe; espelhamento ignorado: $target"
        return 0
    fi

    echo "Espelhando $source -> $target"

    retry "pull de $source" \
        docker pull --platform linux/amd64 "$source"

    docker tag "$source" "$target"

    retry "push de $target" \
        docker push "$target"

    retry "validação de $target" \
        docker manifest inspect "$target"

    docker image rm "$target" "$source" >/dev/null 2>&1 || true

    if (( BETWEEN_IMAGES_DELAY_SECONDS > 0 )); then
        sleep "$BETWEEN_IMAGES_DELAY_SECONDS"
    fi
}

while IFS='|' read -r source target; do
    [[ -n "$source" ]] || continue

    mirror_image \
        "docker.io/library/${source}" \
        "ghcr.io/${GHCR_OWNER}/${target}"
done <<'IMAGES'
php:8.4-fpm-alpine|pdf2ofx-base-php:8.4-fpm-alpine
composer:2.8|pdf2ofx-base-composer:2.8
nginx:1.28-alpine|pdf2ofx-base-nginx:1.28-alpine
python:3.13-slim-bookworm|pdf2ofx-base-python:3.13-slim-bookworm
redis:8-alpine|pdf2ofx-base-redis:8-alpine
postgres:17-alpine|pdf2ofx-base-postgres:17-alpine
IMAGES
