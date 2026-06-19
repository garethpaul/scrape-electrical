# Finite Positive Timeout Validation

Status: Completed

## Problem

`Product` currently checks only `timeout <= 0`. Direct callers can trigger a
raw `TypeError` with nonnumeric values, while booleans, `NaN`, and positive
infinity pass validation and reach `urllib2.open`. The constructor should fail
deterministically before any network setup.

## Requirements

1. Accept positive finite integer, long, and float timeout values.
2. Reject booleans, nonnumeric values, zero, negatives, `NaN`, and both
   infinities with the existing generic timeout error.
3. Validate before assigning the timeout or constructing a network opener.
4. Preserve CLI defaults, source URL validation, redirect policy, response
   limits, database behavior, and request semantics.
5. Add Python 2-compatible tests, mutation-sensitive contracts, and truthful
   guidance.

## Implementation Units

### 1. Harden timeout validation

File:

- `scrape.py`

Add one explicit numeric, non-boolean, positive, finite timeout boundary in the
`Product` constructor.

### 2. Protect hostile inputs

Files:

- `tests/test_scrape.py`
- `scripts/check-docs-plans.py`
- `docs/plans/2026-06-15-finite-positive-timeout-validation.md`

Cover accepted positive values and rejected boolean, string, missing,
nonpositive, `NaN`, and infinite values. Require exact source, tests,
documentation, and completed-plan evidence.

### 3. Document the API contract

Files:

- `AGENTS.md`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Record that scraper timeouts must be finite positive numbers before network
setup.

## Verification Completed

- The focused constructor probe showed that Python 2 accepted `True`, `"1"`,
  `NaN`, and positive infinity before the fix; all hostile values are rejected
  afterward while positive finite integers, longs, and floats remain valid.
- Eight hostile timeout mutations were rejected across boolean, numeric type,
  positivity, `NaN`, infinity, fixture, guidance, and completed-plan contracts.
- repository and external-directory `make check` passed with all 34 Python 2
  database, CLI, network, redirect, response, and parser tests.
- hostile timeout mutations were rejected.
- generated-artifact and credential-pattern audits passed.

## Scope Boundaries

- Do not change the default timeout, request headers, response size, redirect
  behavior, source/product URL handling, database writes, or CLI shape.
- Do not migrate the Python 2 runtime or add dependencies.
- Do not claim live scraping, PostgreSQL, or remote endpoint execution.
- Do not merge or close any pull request without explicit authorization.
