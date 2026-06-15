---
title: Python 3 Offline Compatibility
type: maintenance
status: in_progress
date: 2026-06-15
execution: code
---

# Python 3 Offline Compatibility

## Summary

Make the historical scraper and its complete offline safety suite run on Python
3.12 while retaining the digest-pinned Python 2.7 compatibility lane and all
existing network, parsing, SQL, cleanup, and CLI behavior.

---

## Problem Frame

The maintained gate currently proves behavior only in an archived Python 2.7
container. Production source imports `urllib2` and `urlparse`, tests import
`StringIO` and use a long-integer literal, and the Makefile defaults to
`python2`. These are small compatibility barriers, but they prevent current
Python from executing the already-isolated 34-test offline suite.

The external services are not needed for verification: network responses,
Beautiful Soup, psycopg2, PostgreSQL, and CLI output are already faked or
characterized. A dual-runtime change can therefore raise the supported
verification floor without changing live scraper semantics or installing
unreviewed dependencies.

---

## Requirements

- **R1:** `scrape.py`, workflow contracts, documentation checks, and all offline
  tests must execute on Python 3.12.
- **R2:** The digest-pinned Python 2.7.18 lane and all existing Python 2 behavior
  must remain green.
- **R3:** URL requests, redirects, HTTP errors, string buffers, integer type
  checks, parser output, SQL values, cleanup order, and CLI output must remain
  behaviorally equivalent across both runtimes.
- **R4:** Hosted CI must run the canonical offline gate once on Python 2.7 and
  once on pinned Python 3.12 without installing Beautiful Soup or psycopg2.
- **R5:** Static contracts must reject removal of either runtime, compatibility
  import regressions, runtime-specific test syntax, dependency installation,
  guidance drift, and incomplete plan evidence.
- **R6:** No live site, redirect, parser dependency, database, credential, or
  production deployment may be exercised or changed.

---

## Key Technical Decisions

- **Use standard-library compatibility aliases:** preserve the existing
  `urllib2` call surface internally while importing Python 3 `urllib.request`
  and `urllib.error` under the same compatibility object, minimizing changes to
  hardened request and redirect logic.
- **Keep Python 2 as an explicit archive lane:** Python 3 support supplements
  rather than silently replaces the historical runtime contract.
- **Use one canonical Make gate with a runtime parameter:** local and hosted
  jobs pass the intended interpreter explicitly so both execute the same lint,
  workflow-contract, and test scope.
- **Do not install optional scraper dependencies in CI:** the verification
  remains credential-free and offline; fake modules continue to characterize
  database and parser integration boundaries.

---

## Assumptions

- Python 3.12 is the current maintained runtime for this compatibility layer.
- Python 2.7 behavior is still required only for historical archive confidence,
  not as a recommendation for production deployment.
- Existing use of text strings and byte-counting response fakes represents the
  intended compatibility behavior; no encoding-policy redesign is included.

---

## Implementation Units

### U1. Add Runtime-Compatible Standard Library Boundaries

**Goal:** Allow production source and tests to import and execute on both
Python 2.7 and Python 3.12 without changing public behavior.

**Requirements:** R1, R2, R3, R6

**Dependencies:** None

**Files:**

- `scrape.py`
- `tests/test_scrape.py`

**Approach:** Add narrow import fallbacks for URL request/error/parsing modules
and in-memory text buffers, define one cross-runtime integer-type tuple, and
remove Python-2-only literal syntax. Keep existing names and test assertions so
the behavioral diff remains limited to compatibility boundaries.

**Execution note:** Run the current suite under Python 3 first and preserve its
import/syntax failures as the regression baseline.

**Test scenarios:**

- Both runtimes execute all current scraper tests with identical counts.
- Redirect rejection still raises the runtime's HTTP error type through the
  existing `scrape.urllib2` test surface.
- Integer and long-equivalent timeout/response limits remain accepted while
  booleans, non-integral values, NaN, infinities, and nonpositive values remain
  rejected.
- Dry-run output remains text and database/parser fakes require no external
  package installation.

**Verification:** All scraper tests pass under Python 2.7 and Python 3.12 with
no assertion changes that weaken safety boundaries.

### U2. Add The Canonical Python 3 Hosted Lane

**Goal:** Make current-Python compatibility durable in local and hosted gates.

**Requirements:** R1, R2, R4, R5, R6

**Dependencies:** U1

**Files:**

- `Makefile`
- `.github/workflows/check.yml`
- `scripts/workflow_contract.py`
- `scripts/test_workflow_contract.py`

**Approach:** Keep the reviewed Python 2 container job and add a Python 3.12
Ubuntu job using the already pinned checkout action and a pinned setup-python
action. Run `make check` with the target interpreter explicitly in both lanes.
Extend workflow contracts so neither lane, immutable action pin, read-only
permission, timeout, credential isolation, nor dependency-free execution can
be removed independently.

**Test scenarios:**

- The exact two-job workflow passes validation.
- Removing, duplicating, floating, or weakening either runtime lane fails.
- Adding package installation or `continue-on-error` to either job fails.
- Both jobs execute the same canonical gate with their declared interpreter.

**Verification:** Workflow contract mutations and both runtime gates prove the
same offline scope is authoritative.

### U3. Maintain The Dual-Runtime Contract

**Goal:** Document the compatibility boundary and prevent drift back to a
Python-2-only repository.

**Requirements:** R1, R2, R3, R4, R5, R6

**Dependencies:** U1, U2

**Files:**

- `scripts/check-docs-plans.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `AGENTS.md`
- `docs/plans/2026-06-15-python3-compatibility.md`

**Approach:** Replace Python-2-only source assertions with explicit dual-runtime
compatibility contracts, synchronize contributor and security guidance, and
require this plan to retain completed verification evidence.

**Test scenarios:**

- Removing the Python 3 import fallback, integer compatibility type, or
  Python-3-safe buffer/test syntax is rejected.
- Removing either hosted lane or changing documentation back to Python 2-only
  is rejected.
- Reverting plan status or verification evidence is rejected.

**Verification:** Repository and external-directory gates pass under both
runtimes, and isolated hostile mutations fail for their intended contract
messages.

---

## Scope Boundaries

- Do not upgrade Beautiful Soup, psycopg2, PostgreSQL, or scraper targets.
- Do not execute live HTTP requests, redirects, HTML parsing, database writes,
  credentials, or deployment.
- Do not remove or republish the Python 2 archive lane.
- Do not redesign text/byte encoding, parser schemas, SQL shape, or CLI output.

### Deferred to Follow-Up Work

- Replace the unpinned dependency declarations with a separately reviewed,
  current-Python dependency and packaging strategy before live deployment.
- Retire the archived Python 2 lane only through an explicit repository-owner
  decision after Python 3 behavior has remained stable.

---

## Risks And Dependencies

- Python 2 and Python 3 expose URL modules differently; aliases must preserve
  both the request API and HTTP error type used by redirect tests.
- Text versus bytes behavior can diverge around real HTTP bodies, so this change
  claims offline compatibility only and retains live-network validation as a
  separate boundary.
- Adding a hosted lane increases runner use but provides the first authoritative
  current-runtime signal for every existing safety test.
