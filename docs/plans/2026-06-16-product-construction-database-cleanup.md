# Close Database Resources When Product Construction Fails

Status: Completed

## Context

The CLI opens the selected database before `Product` validates the source URL,
timeout, and response-size limit. If that constructor rejects an invalid value,
`Product.find()` never starts and its database cleanup block cannot run.

## Requirements

- Close the database when `Product` construction raises.
- Preserve the original validation exception after cleanup succeeds.
- Keep normal cleanup owned by `Product.find()` without double-closing.
- Cover source URL, timeout, and response-limit constructor failures.
- Add a static contract that rejects removal or reordering of the cleanup path.
- Keep validation offline and compatible with Python 2.7 and Python 3.12.

## Intended Files

- `scrape.py`
- `tests/test_scrape.py`
- `scripts/check-docs-plans.py`
- `README.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-product-construction-database-cleanup.md`

## Verification

- 46 tests passed under Python 2.7 and Python 3.12, including source URL,
  timeout, response-limit, and successful single-close ownership cases.
- The repository and external-directory `make check` passed under both runtimes.
- Four hostile construction-cleanup mutations were rejected on both runtimes:
  removed cleanup, swallowed validation failure, double cleanup after success,
  and removed constructor exception handling.
- Exact diff, generated-artifact and credential-pattern audits passed.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.
