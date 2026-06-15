# Finite Positive Timeout Validation

Status: Planned

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

## Verification Plan

- Run the focused timeout tests before implementation and confirm hostile
  values expose the current gap.
- Run Python 2 `make check` from the repository and an external directory with
  explicit timeouts.
- Reject isolated mutations for type, boolean, positivity, finiteness, tests,
  documentation, and completed-plan evidence.
- Audit the exact diff, bytecode, generated artifacts, changed-line secrets,
  and intended paths before commit.

## Scope Boundaries

- Do not change the default timeout, request headers, response size, redirect
  behavior, source/product URL handling, database writes, or CLI shape.
- Do not migrate the Python 2 runtime or add dependencies.
- Do not claim live scraping, PostgreSQL, or remote endpoint execution.
- Do not merge or close any pull request without explicit authorization.
