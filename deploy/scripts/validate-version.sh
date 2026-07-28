#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

VERSION="$(tr -d '[:space:]' < VERSION)"

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
    echo "ERRO: versão inválida em VERSION: $VERSION" >&2
    exit 1
fi

assert_contains() {
    local file="$1"
    local expected="$2"

    if ! grep -Fq -- "$expected" "$file"; then
        echo "ERRO: $file não contém: $expected" >&2
        exit 1
    fi
}

assert_not_contains() {
    local file="$1"
    local forbidden="$2"

    if grep -Fq -- "$forbidden" "$file"; then
        echo "ERRO: $file contém conteúdo proibido: $forbidden" >&2
        exit 1
    fi
}

assert_contains services/converter/pyproject.toml "version = \"$VERSION\""
assert_contains services/converter/src/pdf2ofx/__init__.py "__version__ = \"$VERSION\""
assert_contains .env.example "pdf2ofx-app:$VERSION"
assert_contains .env.example "pdf2ofx-gateway:$VERSION"
assert_contains .env.example "pdf2ofx-converter:$VERSION"
assert_contains .env.production.example "pdf2ofx-app:$VERSION"
assert_contains .env.production.example "pdf2ofx-gateway:$VERSION"
assert_contains .env.production.example "pdf2ofx-converter:$VERSION"
assert_contains deploy/docker/.env.example "PDF2OFX_VERSION=$VERSION"
assert_contains deploy/docker/.env.example "pdf2ofx-app:$VERSION"
assert_contains deploy/docker/.env.example "pdf2ofx-gateway:$VERSION"
assert_contains deploy/docker/.env.example "pdf2ofx-converter:$VERSION"
assert_contains deploy/docker/install.sh "VERSION=\"$VERSION\""
assert_contains deploy/docker/README.md "--version $VERSION"
assert_contains deploy/dockge/pdf2ofx/.env.example "PDF2OFX_VERSION=$VERSION"
assert_contains deploy/dockge/pdf2ofx/.env.example "pdf2ofx-app:$VERSION"
assert_contains deploy/dockge/pdf2ofx/.env.example "pdf2ofx-gateway:$VERSION"
assert_contains deploy/dockge/pdf2ofx/.env.example "pdf2ofx-converter:$VERSION"
assert_contains deploy/dockge/install-vps.sh "APP_VERSION=\"$VERSION\""
assert_contains deploy/dockge/README.md "--version $VERSION"
assert_contains docs/DEPLOYMENT.md "--version $VERSION"
assert_contains README.md "\`$VERSION\`"
assert_contains CHANGELOG.md "## [$VERSION]"

assert_contains apps/web/docker/Dockerfile "ARG REDIS_EXTENSION_VERSION=6.3.0"
assert_contains apps/web/docker/Dockerfile 'phpredis/archive/refs/tags/${REDIS_EXTENSION_VERSION}.tar.gz'
assert_contains apps/web/docker/Dockerfile "COPY apps/web/public /var/www/html/public"
assert_contains .github/workflows/release.yml 'pdf2ofx-docker-deployment-${VERSION}.zip'
assert_contains .github/workflows/release.yml 'pdf2ofx-dockge-deployment-${VERSION}.zip'
assert_not_contains apps/web/docker/Dockerfile "pecl install redis"
assert_not_contains apps/web/docker/Dockerfile "COPY --from=app /var/www/html/public"
assert_contains .github/workflows/ci.yml 'bash deploy/scripts/validate-gateway-image.sh "${{ matrix.image }}:${GITHUB_SHA}"'
assert_contains deploy/scripts/validate-gateway-image.sh '--add-host app:127.0.0.1'
assert_contains deploy/scripts/validate-gateway-image.sh 'http://127.0.0.1:8080/health'
assert_contains deploy/dockge/tests/test-install-vps.sh 'run_as_root env'
assert_contains deploy/dockge/tests/test-install-vps.sh '"PATH=$TEMP_DIR/bin:$PATH"'
assert_contains deploy/dockge/tests/test-install-vps.sh 'sem acesso ao daemon real'
assert_contains .github/workflows/ci.yml 'Preparar ambiente de testes Laravel'
assert_contains .github/workflows/ci.yml 'test -f .env.example'
assert_contains .github/workflows/ci.yml 'cp -- .env.example .env'
assert_contains .github/workflows/ci.yml 'Validar estrutura do Laravel'
assert_contains apps/web/.env.example 'APP_ENV=local'
assert_contains apps/web/.env.example 'DB_CONNECTION=pgsql'
assert_contains apps/web/.env.example 'CONVERTER_BASE_URL=http://converter-api:8000'

for required in \
    deploy/docker/compose.yaml \
    deploy/docker/docker-compose.yml \
    deploy/docker/.env.example \
    deploy/docker/README.md \
    deploy/docker/install.sh \
    deploy/docker/deploy.sh \
    deploy/docker/update.sh \
    deploy/docker/rollback.sh \
    deploy/docker/backup.sh \
    deploy/docker/restore.sh \
    deploy/docker/healthcheck.sh \
    deploy/docker/status.sh \
    deploy/docker/logs.sh \
    deploy/docker/cloudpanel/reverse-proxy.conf.example \
    deploy/docker/systemd/pdf2ofx.service \
    deploy/dockge/README.md \
    deploy/dockge/install-vps.sh \
    deploy/dockge/dockge/compose.yaml \
    deploy/dockge/dockge/.env.example \
    deploy/dockge/pdf2ofx/compose.yaml \
    deploy/dockge/pdf2ofx/.env.example \
    deploy/dockge/scripts/healthcheck.sh \
    deploy/dockge/scripts/post-deploy.sh \
    deploy/dockge/scripts/update-version.sh \
    deploy/dockge/scripts/backup.sh \
    deploy/dockge/scripts/logs.sh \
    deploy/dockge/scripts/status.sh \
    deploy/dockge/tests/test-install-vps.sh \
    deploy/dockge/cloudpanel/pdf2ofx-reverse-proxy.conf.example \
    deploy/dockge/cloudpanel/dockge-reverse-proxy.conf.example \
    docs/DOCKGE.md \
    deploy/scripts/validate-gateway-image.sh \
    apps/web/.env.example; do
    if [[ ! -f "$required" ]]; then
        echo "ERRO: arquivo obrigatório de implantação não encontrado: $required" >&2
        exit 1
    fi
done


if ! cmp -s deploy/docker/compose.yaml deploy/docker/docker-compose.yml; then
    echo "ERRO: deploy/docker/compose.yaml e docker-compose.yml estão divergentes." >&2
    exit 1
fi

if [[ ! -f "docs/VALIDATION-${VERSION}.md" ]]; then
    echo "ERRO: relatório docs/VALIDATION-${VERSION}.md não encontrado." >&2
    exit 1
fi

if [[ ! -f "docs/PULL_REQUEST-${VERSION}.md" ]]; then
    echo "ERRO: documentação docs/PULL_REQUEST-${VERSION}.md não encontrada." >&2
    exit 1
fi

echo "Metadados e pacote de implantação da versão $VERSION validados."
