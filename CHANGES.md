# Changes

## 2026-06-26 02:02 PDT - P1 - Skip empty product prices

### Summary

Prevented empty or whitespace-only plain and nested bold prices from reaching
PostgreSQL or dry-run output while preserving later valid product rows.

### Work completed

- Reproduced three incomplete price variants being inserted.
- Added a Python 2/3-compatible nonblank price guard after bold-price selection.
- Added a focused mocked regression, completed plan, guidance, and static contracts.

### Threads

- None; parser branches and offline coverage were reviewed directly.

### Files changed

- `scrape.py` — reject non-string and blank selected prices.
- `tests/test_scrape.py` — empty plain/bold price continuation regression.
- README, security, vision, agent guidance, plan, checker, and changelog.

### Validation

- RED focused suite — inserted three incomplete rows before the fix.
- Full offline suites on Python 2.7 and Python 3.12 — passed 66 tests.
- Repository and external-directory `make check` on both runtimes — passed.
- Five isolated hostile mutations — all rejected.
- Python compilation and `git diff --check` — passed.
- Generic Python 3.12 Docker attempt — stopped in the pre-existing Make authority
  harness under GNU Make 4.4.1; isolated Python 3.12 with hosted-compatible GNU
  Make 4.3 passed both complete gates.

### Bugs / findings

- P1 correctness: remote empty price markup could create incomplete database rows.

### Blockers

- None; no live network or database validation is required for this boundary.

### Next action

- Complete exact-head review, hosted dual-runtime CI, CodeQL, and merge.

## 2026-06-26 06:25 - P2 - Reject non-string URL values safely

### Summary

Added a Python 2/3-compatible non-string URL guard so malformed caller or
parser values cannot abort a scrape through an unexpected `.strip()` failure.

### Work completed

- Rejected non-string source URL values with the existing sanitized error.
- Skipped non-string parsed product links while preserving later safe rows.
- Added regression coverage for booleans, integers, lists, and arbitrary
  objects without echoing rejected source values.
- Raised the complete offline-suite contract from 63 to 65 tests under Python
  2.7 and Python 3.12.

### Threads

- Started: non-string URL normalization boundary.
- Continued: continuous open-source maintenance loop.
- Stopped: none.

### Files changed

- `scrape.py`
- `tests/test_scrape.py`
- `scripts/check-docs-plans.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `docs/plans/2026-06-25-non-string-url-guard.md`

## 2026-06-26 06:08 - P1 - Define responsible scraping boundaries

### Summary

Closed the permission, request-rate, and data-retention roadmap item with a
standards-backed operator guide and a Python 2/3 documentation contract.

### Work completed

- Required written target-owner approval with explicit host, path, purpose,
  window, request budget, field, storage, contact, and retention scope.
- Distinguished RFC 9309 robots rules from authorization.
- Documented serial requests, `Retry-After`, fail-closed stop conditions, data
  minimization, raw-response deletion, and derived-row retention boundaries.
- Linked the guide from usage and security documentation and removed the
  completed roadmap item.
- Corrected the frozen offline-suite count from 51 to the 63 tests the current
  gate actually executes.

### Threads

- Started: responsible-use documentation contract.
- Continued: continuous open-source maintenance loop.
- Stopped: none.

### Files changed

- `RESPONSIBLE_USE.md` — permission, pacing, stop, and retention checklist.
- `README.md` and `SECURITY.md` — operator-facing guide links.
- `VISION.md` — completed roadmap state.
- `scripts/check-docs-plans.py` — durable guide contract.
- `docs/plans/2026-06-25-responsible-scraping-guide.md` — implementation plan.
- `CHANGES.md` — this maintenance-cycle record.

### Validation

- Red contract run — failed for the missing guide, plan, links, required
  boundaries, and stale roadmap item before documentation was added.
- Pinned Python 2.7 `make check` — passed all 63 offline tests with 11 expected
  real-parser dependency skips, 21 workflow mutations, and Make authority gates.
- Python 3 `make check` — passed all 63 offline tests, 21 workflow mutations,
  documentation contracts, and Make authority gates.
- Thirteen isolated hostile documentation mutations — all rejected, including
  removal of permission, pacing, `Retry-After`, stop, retention, deletion,
  personal-data, guide-link, roadmap, and 63-test-count promises.

### Bugs / findings

- P1: Existing guidance said to confirm permission and rate limits but did not
  define approval scope, stop conditions, retention, or deletion evidence.
- P1: Existing guidance did not clarify that robots rules are not authorization
  or explain server-directed `Retry-After` handling.
- P2: README and its contract still claimed 51 offline tests after the suite had
  grown to 63, allowing verification documentation to drift from actual output.
- P2: The initial `Retry-After` assertion accepted the RFC URL after all prose
  guidance was removed; a hostile mutation exposed and fixed that false positive.

### Blockers

- No live target permission, HTTP requests, or PostgreSQL credentials are
  available or required; verification remains fully offline.

### Next action

- Open an exact-head PR, require hosted Python 2.7/Python 3.12 and CodeQL gates,
  then review and merge if clean.

## 2026-06-25

- Excluded script and style descendants before normalizing product-title text,
  including when BeautifulSoup selects html5lib, with parser-variant regression coverage.

## 2026-06-22

- Extracted complete product-title text from nested and mixed anchor markup in
  document order, preserving source adjacency while normalizing existing
  whitespace runs. Added real BeautifulSoup parser-variant and portable hostile-
  mutation coverage, and skipped titles that normalize to empty without requiring
  a live site or PostgreSQL server.

## 2026-06-21

- Isolated Make verification authority while preserving exact `python2` and
  `python3` selection, with 77 successful target/authority cases and 21
  rejected runtime, function, preload, and Makefile-list cases.
- Added a deferred final-file-set guard so a later `-f` Makefile cannot replace
  a public target, selected `sed` only from trusted fixed locations, and removed
  the fixed `dirname` dependency from root resolution.

## 2026-06-19

- Closed rejected redirect response bodies before raising sanitized same-host
  redirect errors, removing Python 3 `ResourceWarning` leakage from blocked
  redirect paths.

## 2026-06-17

- Added Product construction primary error preservation so validation and
  interruption failures survive secondary database-close errors.
- Closed PostgreSQL connections when cursor construction fails, while
  preserving the original cursor error if connection cleanup also fails.

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
