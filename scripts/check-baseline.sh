#!/usr/bin/env bash
set -euo pipefail

if grep -R "from lib import url" -n scrape.py; then
  echo "scrape.py must not depend on an untracked local lib module" >&2
  exit 1
fi

python3 - <<'PY'
from pathlib import Path

source = Path("scrape.py").read_text()
if "from lib import url" in source:
    raise SystemExit("missing lib import is still present")
PY
