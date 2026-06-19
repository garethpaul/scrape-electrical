---
title: Close Database Connections When Cursor Construction Fails
type: fix
date: 2026-06-17
---

# Close Database Connections When Cursor Construction Fails

Status: Completed

## Context

`Database` opens a PostgreSQL connection before it creates the cursor. If
cursor construction raises, no `Database` instance reaches `close()`, so the
new connection remains open. This differs from the established cursor-first
cleanup path because construction never completes.

## Requirements

- R1. Attempt connection cleanup when cursor construction raises after a
  successful connection.
- R2. Preserve the original cursor-construction exception when connection
  cleanup also raises.
- R3. Leave successful construction and the existing cursor-first `close()`
  behavior unchanged.
- R4. Cover the failure paths without a live PostgreSQL service under Python
  2.7 and Python 3.12.
- R5. Add a static contract and hostile mutations that reject removal or
  weakening of the constructor cleanup boundary.

## Scope Boundaries

- Do not change database credentials, SQL behavior, transaction handling, or
  the public constructor signature.
- Do not add runtime dependencies or require network or database access.

## Implementation Units

### U1. Characterize cursor-construction failure

- **Goal:** Prove the acquired connection leaks when `cursor()` raises and
  define primary-error preservation when cleanup also fails.
- **Files:** `tests/test_scrape.py`
- **Verification:** Focused offline unit tests under both supported runtimes.

### U2. Close partially constructed database resources

- **Goal:** Attempt connection cleanup around cursor acquisition while
  preserving the cursor failure and successful-construction behavior.
- **Files:** `scrape.py`
- **Verification:** Focused unit tests plus the complete repository gate.

### U3. Make the boundary durable

- **Goal:** Record the behavior in project documentation and make structural
  regressions fail closed.
- **Files:** `scripts/check-docs-plans.py`, `README.md`, `CHANGES.md`,
  `docs/plans/2026-06-17-database-cursor-construction-cleanup.md`
- **Verification:** Repository-root and external-directory `make check` under
  Python 2.7 and Python 3.12, followed by hostile mutation checks.

## Verification

- 48 tests passed under Python 2.7 and Python 3.12, including cleanup-attempt
  and primary-error preservation cases.
- The repository and external-directory `make check` passed under both runtimes.
- Four hostile database-constructor cleanup mutations were rejected under both
  runtimes: removed cleanup, swallowed cursor failure, removed cleanup-error
  suppression, and removed the cursor acquisition guard.
- Exact-diff, generated-artifact and credential-pattern audits passed.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.
