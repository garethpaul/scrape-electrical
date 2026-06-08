# Scrape Electrical Baseline

## Status: Completed

## Context

`scrape-electrical` is a legacy Python 2 scraper/database prototype. The
maintenance baseline should preserve parser and SQL safety improvements while
making responsible scraping expectations visible in tests and docs.

## Objectives

- Keep database credentials caller-provided and out of source control.
- Validate parameterized SQL inserts and table-name safety.
- Cover supported product price markup shapes without network access.
- Avoid spoofed request headers that imply anti-blocking or evasion behavior.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs Python 2 syntax checks and mocked unit tests.
- Added a plain request-building contract so the scraper no longer sets a fake
  referer, browser user agent, or random DNT header.
- Added canonical `docs/plans` coverage and a Python 2 docs-plan checker under
  `make lint`.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `python2 -m py_compile scrape.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add CLI argument parsing and a dry-run mode before live database writes.
- Document target-site permission, rate limits, and data retention before any
  production use.
