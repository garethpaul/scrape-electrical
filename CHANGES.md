# Changes

## 2026-06-08

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
