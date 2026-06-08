# Changes

## 2026-06-08

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
