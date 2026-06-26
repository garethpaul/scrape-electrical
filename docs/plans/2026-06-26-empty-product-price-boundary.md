# Empty Product Price Boundary

Status: Completed

## Problem

`Product.product_fields` rejected a missing price element but accepted empty or
whitespace-only price text. Empty plain spans and empty nested bold prices were
therefore inserted as incomplete database rows.

## Scope

- Reject non-string, empty, and whitespace-only selected price text.
- Apply the boundary after the existing bold-price preference.
- Preserve the original formatting of valid nonblank prices.
- Continue parsing later safe product rows.
- Use only mocked HTML and database fixtures; do not perform live scraping.

## Work Completed

- Added one focused regression covering empty plain, whitespace-only plain, and
  empty bold prices followed by a valid row.
- Added a Python 2/3-compatible string and nonblank guard before insertion.
- Added static source/test, project guidance, and completed-plan contracts.

## Verification Completed

- RED focused test inserted all three incomplete rows before the guard.
- 66 tests passed under Python 2.7 and Python 3.12.
- The repository and external-directory `make check` passed under both runtimes.
- Five isolated hostile mutations were rejected across the source guard,
  regression, guidance, plan status, and verification evidence.
- Python compilation and `git diff --check` passed.
- No live HTTP, HTML fetching, PostgreSQL, credentials, or deployment was exercised.
- The generic Python 3.12 Docker image bundled GNU Make 4.4.1 and stopped in the
  pre-existing Make authority harness; the supported current lane was rerun
  successfully with isolated Python 3.12 and GNU Make 4.3, matching hosted CI.

## Residual Risk

The scraper intentionally preserves visible price formatting and does not parse
currency or numeric value semantics. Rate limiting remains separate future work
before any broad authorized live scraping.
