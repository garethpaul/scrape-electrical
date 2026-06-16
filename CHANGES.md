# Changes

## 2026-06-16

- Closed database resources when source URL, timeout, or response-limit
  validation fails after CLI database construction.
- Advertised HTML source responses and rejected explicit non-HTML content types
  before reading response bodies, while preserving missing-header compatibility.
- Required identity content encoding for source requests and rejected responses
  declaring any other content encoding before body reads.
- Completed bounded response reads across legal short chunks so fragmented
  pages are not truncated and oversized fragmented bodies remain rejected.

## 2026-06-15

- Added dependency-free offline compatibility for Python 2.7 and Python 3.12,
  with matching local and hosted verification lanes.
- Scraper timeouts must be finite positive numbers before network setup.
- Rejected malformed source URL authorities before opener construction without
  disclosing the supplied URL.

## 2026-06-14

- Rejected malformed product links at the row boundary while continuing to
  process later safe products.

## 2026-06-13

- Rejected product link credentials parsed from remote markup before database
  writes or dry-run output while continuing to process safe products.
- Rejected source URL credentials before initial request construction, with
  non-disclosing Python 2 regression coverage.
- Added an explicit redirect hop limit of five total redirects and two repeats
  of the same target, with Python 2 regression coverage.

## 2026-06-12

- Added a configurable 5 MiB response body size limit with exact-boundary,
  oversized-read, closure, validation, and CLI-forwarding coverage.
- Added a same-host redirect boundary that permits relative paths and HTTPS
  upgrades while rejecting cross-host, alternate-port, downgrade, non-web,
  hostless, or credential targets.

## 2026-06-10

- Closed scraper HTTP responses after successful and failed body reads, with
  Python 2 regression coverage.
- Added a least-privilege GitHub Actions workflow that runs the complete
  offline `make check` gate with credential-free checkout pinned by commit.
- Replaced the prepared Python 3 skip path with the complete offline tests in a
  digest-pinned Python 2.7.18 container.
- Made the canonical gate independent of the caller's current directory.
- Added exact workflow-policy validation and 17 hostile mutations covering
  triggers, credentials, actions, permissions, runner, timeout, image digest,
  failure handling, runtime proof, dependency installation, and commands.

## 2026-06-09

- Kept Python verification bytecode-free and added checker coverage to reject
  generated `.pyc` and `.pyo` files.
- Rejected blank, hostless, and non-HTTP(S) source page URLs before `urllib2`
  reads, with Python 2 regression coverage.
- Added a Python 2 command-line entry point with dry-run output and complete
  database credential requirements for live writes.
- Added product-link normalization so relative URLs resolve against the source
  page and non-HTTP(S) links are skipped before database insertion.
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
