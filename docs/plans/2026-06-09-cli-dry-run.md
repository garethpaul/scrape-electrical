# CLI Dry-Run Guard

## Status: Completed

## Context

`scrape-electrical` had a parser and database implementation, but no direct
command-line entry point. Operators needed ad hoc driver code, and there was no
repository-level guard that a live run must either be a dry-run preview or
provide complete PostgreSQL connection fields.

## Objectives

- Add a Python 2 compatible CLI for the checked-in scraper.
- Provide a `--dry-run` mode that prints parsed rows instead of opening a
  database connection.
- Reject live command-line writes unless all database connection fields are
  provided explicitly.
- Preserve the existing importable `main(database, url)` contract.

## Work Completed

- Added `argparse` parsing for source URL, timeout, dry-run, database fields,
  and target table name.
- Added `DryRunDatabase` as a write-free sink for parser output.
- Centralized CLI database creation so dry-run bypasses PostgreSQL and live
  writes require complete credentials.
- Added Python 2 tests for dry-run parsing, dry-run output, missing live
  credentials, and live database construction.
- Extended `scripts/check-docs-plans.py` to preserve the CLI dry-run contract.
- Updated README, VISION, and CHANGES.

## Verification

- `python2 -m py_compile scrape.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add rate limiting or backoff before broad live scraping.
- Document target-site permission, rate limits, and data retention expectations
  for any recurring use.
