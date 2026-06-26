# Preserve Response Read Primary Errors

Status: Completed

## Problem

`Product.read()` closed the HTTP response in an unconditional `finally` block.
If body processing raised and `response.close()` also raised, Python replaced
the transport, validation, or interruption failure with the cleanup error.

## Decision

Track whether response processing failed. During an active primary failure,
attempt close in a separate Python 2-compatible helper frame and suppress only
that secondary close error before the bare re-raise completes. After a
successful read, call `response.close()` normally so a standalone cleanup
failure remains visible.

## Scope

- `scrape.py`
- `tests/test_scrape.py`
- `scripts/check-docs-plans.py`
- `README.md`, `SECURITY.md`, `VISION.md`, `AGENTS.md`, and `CHANGES.md`

No retry, pacing, parsing, redirect, database, dependency, or workflow behavior
changes in this cycle.

## Verification

- The failing-first regression proved a response-close failure replaced both an
  ordinary read error and `KeyboardInterrupt` before the fix.
- 68 tests passed under Python 2.7 and Python 3.12.
- The repository and external-directory `make check` passed under both runtimes.
- Three hostile response-cleanup mutations were rejected: unconditional close,
  swallowed successful close failure, and narrowed `Exception` handling.
- Documentation, workflow, Make authority, bytecode, generated-artifact,
  credential-pattern, and exact-diff checks passed.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.

The canonical verification command remains `make check`.
