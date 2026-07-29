#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Uso: bash deploy/scripts/release.sh X.Y.Z" >&2
    exit 1
fi

VERSION="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
OLD_VERSION="$(tr -d '[:space:]' < VERSION)"

if [[ "$OLD_VERSION" == "$VERSION" ]]; then
    echo "A versão $VERSION já está declarada no projeto." >&2
    exit 1
fi

python - "$OLD_VERSION" "$VERSION" <<'PY'
from pathlib import Path
import re
import sys

old_version, version = sys.argv[1:]
Path("VERSION").write_text(f"{version}\n")

path = Path("services/converter/pyproject.toml")
path.write_text(
    re.sub(r'^version = "[^"]+"', f'version = "{version}"', path.read_text(), count=1, flags=re.M)
)
Path("services/converter/src/pdf2ofx/__init__.py").write_text(f'__version__ = "{version}"\n')

versioned_files = [
    Path(".env.example"),
    Path(".env.production.example"),
    Path("README.md"),
    Path("docs/DEPLOYMENT.md"),
    Path("deploy/docker/.env.example"),
    Path("deploy/docker/install.sh"),
    Path("deploy/docker/README.md"),
    Path("deploy/dockge/pdf2ofx/.env.example"),
    Path("deploy/dockge/install-vps.sh"),
    Path("deploy/dockge/README.md"),
    Path("deploy/stack/.env.example"),
    Path("deploy/stack/README.md"),
    Path("deploy/stack/VERSION"),
]
for file in versioned_files:
    text = file.read_text()
    file.write_text(text.replace(old_version, version))
PY

cat <<NOTICE
Versão técnica atualizada de ${OLD_VERSION} para ${VERSION}.

Antes do commit, ainda é obrigatório criar:
  docs/VALIDATION-${VERSION}.md
  docs/PULL_REQUEST-${VERSION}.md

e adicionar a seção ${VERSION} ao CHANGELOG.md.
NOTICE

bash deploy/scripts/validate-version.sh || {
    echo "A validação falhou porque a documentação da release ainda precisa ser concluída." >&2
    exit 1
}

git add \
    VERSION \
    services/converter/pyproject.toml \
    services/converter/src/pdf2ofx/__init__.py \
    .env.example \
    .env.production.example \
    README.md \
    docs/DEPLOYMENT.md \
    deploy/docker/.env.example \
    deploy/docker/install.sh \
    deploy/docker/README.md \
    deploy/dockge/pdf2ofx/.env.example \
    deploy/dockge/install-vps.sh \
    deploy/dockge/README.md \
    deploy/stack/.env.example \
    deploy/stack/README.md \
    deploy/stack/VERSION \
    deploy/stack/compose.yaml \
    deploy/stack/scripts \
    deploy/stack/cloudpanel \
    deploy/stack/tests \
    docs/STACK-DEPLOYMENT.md \
    CHANGELOG.md \
    "docs/VALIDATION-${VERSION}.md" \
    "docs/PULL_REQUEST-${VERSION}.md"

git commit -m "chore(release): v${VERSION}"
git tag -a "v${VERSION}" -m "PDF2OFX v${VERSION}"
echo "Release v${VERSION} preparada. Execute: git push origin HEAD --follow-tags"
