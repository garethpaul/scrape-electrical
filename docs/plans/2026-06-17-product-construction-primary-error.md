# Product Construction Primary Error Preservation

## Status: In Progress

## Context

`main()` attempts to close its newly created database when `Product`
construction fails, but it calls `database.close()` directly inside the active
exception handler. A cleanup failure can therefore replace the original URL,
timeout, or response-limit validation error. Construction failures outside
`Exception`, including interruption, also skip cleanup entirely.

## Priority

P1 reliability and diagnostics. The original construction failure explains why
the scraper could not start. Cleanup is required, but a secondary close failure
must not hide that primary error or leave the database open for non-standard
exceptions.

## Objectives

- Attempt database cleanup for every `BaseException` raised while constructing
  `Product`.
- Preserve and re-raise the exact primary construction exception even when
  `database.close()` also fails.
- Keep successful ownership unchanged so `Product.find()` remains responsible
  for its one database close.
- Use a separate helper frame, matching the existing Python 2 constructor
  cleanup pattern, so suppressed cleanup errors cannot replace the active error.
- Add focused dual-runtime and mutation-sensitive coverage.

## Implementation Units

### U1. Preserve construction failures during cleanup

**Goal:** Make product-construction cleanup complete and non-masking.

**Files:** `scrape.py`

**Approach:** Catch `BaseException` around `Product` construction, call a small
cleanup helper that suppresses only close failures while a primary exception is
active, and re-raise the original exception. Leave the successful `p.find()`
path unchanged.

**Verification:** Ordinary validation errors retain identity and message,
interruptions still trigger one close attempt, close failures never replace the
primary error, and successful runs close exactly once through `Product.find()`.

### U2. Add focused regression coverage

**Goal:** Protect primary-error identity and the expanded cleanup boundary.

**Dependencies:** U1

**Files:** `tests/test_scrape.py`

**Approach:** Add a database whose close method fails and assert that source URL
validation still raises the original `ValueError`. Patch `Product` to raise a
`KeyboardInterrupt` during construction and assert the same object is re-raised
after one cleanup attempt. Preserve the existing successful single-close test.

**Verification:** The complete suite passes independently under Python 2.7 and
Python 3, and each focused regression fails when its corresponding guard is
removed.

### U3. Protect source, regression, and evidence contracts

**Goal:** Keep cleanup ordering and primary-error preservation fail closed.

**Dependencies:** U1, U2

**Files:** `scripts/check-docs-plans.py`

**Approach:** Require the helper frame, `BaseException` construction boundary,
focused test names and assertions, documentation phrase, plan reference, and
completed verification evidence.

**Verification:** Hostile mutations that restore `Exception`, inline close,
propagate cleanup failure, remove either regression, weaken documentation, or
falsify completion are rejected.

### U4. Synchronize lifecycle guidance

**Goal:** Document which error remains authoritative when startup cleanup also
fails.

**Dependencies:** U1, U2, U3

**Files:** `README.md`, `VISION.md`, `SECURITY.md`, `CHANGES.md`,
`docs/plans/2026-06-17-product-construction-primary-error.md`

**Approach:** Record that product-construction cleanup covers all primary
exceptions and preserves the primary error over secondary close failures.

**Verification:** Repository and external-directory `make check` pass under
both runtimes, and guidance drift fails the static contract.

## Scope Boundary

- Do not change successful product parsing, inserts, commits, or normal close
  ownership.
- Do not add retries, rollback policy, live PostgreSQL access, or new database
  abstractions.
- Do not modernize Python syntax beyond the existing Python 2/3-compatible
  style.
- Keep PR #19 and its predecessors open and preserve base-first stack ordering.

## Risks

- Catching `BaseException` is appropriate only because cleanup is followed by
  an immediate bare re-raise; the helper must not swallow the primary error.
- Calling cleanup from the same frame can still mask the active exception on
  Python 2, so the separate helper is part of the correctness boundary.

## Work Completed

- Pending implementation.

## Verification

- Pending implementation and validation.
