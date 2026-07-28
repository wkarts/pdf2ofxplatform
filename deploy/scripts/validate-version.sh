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

assert_contains services/converter/pyproject.toml "version = \"$VERSION\""
assert_contains services/converter/src/pdf2ofx/__init__.py "__version__ = \"$VERSION\""
assert_contains .env.example "pdf2ofx-app:$VERSION"
assert_contains .env.example "pdf2ofx-gateway:$VERSION"
assert_contains .env.example "pdf2ofx-converter:$VERSION"
assert_contains .env.production.example "pdf2ofx-app:$VERSION"
assert_contains .env.production.example "pdf2ofx-gateway:$VERSION"
assert_contains .env.production.example "pdf2ofx-converter:$VERSION"
assert_contains README.md "\`$VERSION\`"
assert_contains CHANGELOG.md "## [$VERSION]"

if [[ ! -f "docs/VALIDATION-${VERSION}.md" ]]; then
    echo "ERRO: relatório docs/VALIDATION-${VERSION}.md não encontrado." >&2
    exit 1
fi

if [[ ! -f "docs/PULL_REQUEST-${VERSION}.md" ]]; then
    echo "ERRO: documentação docs/PULL_REQUEST-${VERSION}.md não encontrada." >&2
    exit 1
fi

echo "Metadados da versão $VERSION validados."
