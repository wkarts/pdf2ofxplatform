#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Uso: $0 X.Y.Z" >&2
    exit 1
fi

VERSION="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

printf '%s\n' "$VERSION" > VERSION
python - "$VERSION" <<'PY'
from pathlib import Path
import re
import sys

version = sys.argv[1]
path = Path("services/converter/pyproject.toml")
path.write_text(
    re.sub(r'^version = "[^"]+"', f'version = "{version}"', path.read_text(), count=1, flags=re.M)
)
path = Path("services/converter/src/pdf2ofx/__init__.py")
path.write_text(f'__version__ = "{version}"\n')
PY

git add VERSION services/converter/pyproject.toml services/converter/src/pdf2ofx/__init__.py
git commit -m "chore(release): v${VERSION}"
git tag -a "v${VERSION}" -m "PDF2OFX v${VERSION}"
echo "Release v${VERSION} preparada. Execute: git push origin HEAD --follow-tags"
