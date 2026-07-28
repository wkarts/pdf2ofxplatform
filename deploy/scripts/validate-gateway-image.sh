#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || -z "${1:-}" ]]; then
    echo "Uso: bash deploy/scripts/validate-gateway-image.sh NOME_DA_IMAGEM" >&2
    exit 1
fi

IMAGE="$1"
CONTAINER_NAME="pdf2ofx-gateway-validation-${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}-$$"

cleanup() {
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# O upstream `app:9000` existe somente na rede do Docker Compose. Durante uma
# validação isolada da imagem, registramos o mesmo hostname para que o NGINX
# consiga carregar a configuração sem mascarar erros reais de sintaxe.
docker run --rm \
    --add-host app:127.0.0.1 \
    --entrypoint nginx \
    "$IMAGE" \
    -t

# Além do teste sintático, inicia o container e confirma o endpoint local de
# saúde. A rota /health não depende do PHP-FPM e deve responder mesmo com o
# backend indisponível durante esta validação isolada.
docker run -d \
    --name "$CONTAINER_NAME" \
    --add-host app:127.0.0.1 \
    "$IMAGE" >/dev/null

for attempt in $(seq 1 20); do
    response="$(docker exec "$CONTAINER_NAME" wget -qO- http://127.0.0.1:8080/health 2>/dev/null || true)"
    if [[ "$response" == "ok" ]]; then
        echo "Gateway validado: configuração NGINX e endpoint /health aprovados."
        exit 0
    fi

    if ! docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null | grep -Fxq true; then
        echo "ERRO: o container do gateway encerrou durante a validação." >&2
        docker logs "$CONTAINER_NAME" >&2 || true
        exit 1
    fi

    sleep 1
done

echo "ERRO: o endpoint /health do gateway não respondeu dentro do prazo." >&2
docker logs "$CONTAINER_NAME" >&2 || true
exit 1
