#!/usr/bin/env bash
set -euo pipefail

python3 -B - <<'PY'
from pathlib import Path

source = Path("scrape.py").read_text()
compile(source, "scrape.py", "exec")

checks = [
    "VALID_IDENTIFIER = re.compile",
    "def quote_identifier(identifier):",
    "self.tbname = quote_identifier(tbname)",
    "VALUES (%%s, %%s, %%s)",
    "(name, link, price.replace('$', ''))",
]

for expected in checks:
    if expected not in source:
        raise SystemExit("Missing expected SQL safety code: %s" % expected)

if '" + name + "' in source or "' + name + '" in source:
    raise SystemExit("Product values must not be concatenated into SQL")
PY
