# Changes

## 2026-06-09

- Ensured database connection cleanup is attempted even when cursor cleanup
  fails, with Python 2 regression coverage.
- Closed scraper database cursors before connections and added Python 2
  regression coverage for DB-API cleanup order.
- Switched `Database` initialization to pass PostgreSQL connection fields to
  `psycopg2.connect` as keyword arguments instead of an interpolated connection
  string.
- Added Python 2 unit coverage and a static check for structured database
  connection parameters.

## 2026-06-08

- Skipped product cards with missing or blank links and added parser coverage
  for incomplete anchors.
- Added a bounded default network timeout for product reads with Python 2 unit
  coverage.
- Added `make check` as the shared repository verification alias.
- Added mocked parser coverage for nested `<b>` prices, plain price spans, and
  incomplete product rows.
- Fixed `Product.find()` so products are inserted for both price markup shapes
  without relying on a broad `except` path.
- Added Python 2 unit tests for SQL insert behavior without live network or
  PostgreSQL connections.
- Made `scrape.py` importable without optional scraper/database dependencies
  installed.
- Replaced string-built insert values with parameterized SQL and validated table
  names.
- Added `make verify`, dependency notes, and Python bytecode ignores.
- Removed spoofed request headers from the default fetch path and added unit
  coverage for plain request construction.
- Added canonical `docs/plans` coverage and a Python 2 docs-plan checker under
  `make check`.
