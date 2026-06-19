# Rejected Redirect Response Cleanup

## Status: Completed

## Context

Rejected redirects are raised as sanitized `HTTPError` objects so unsafe target
URLs are not opened or echoed. On Python 3, the rejected error object can retain
the redirect response body until garbage collection, producing a
`ResourceWarning` and delaying cleanup. The same-host policy should fail closed
without leaving response resources for finalizers.

## Priority

P1 reliability and resource hygiene. A blocked redirect should close its
response body before the sanitized redirect error leaves the handler.

## Objectives

- Close the rejected redirect response body before raising the sanitized
  `HTTPError`.
- Keep the redacted error filename and message unchanged.
- Preserve the existing same-host, scheme, port, downgrade, userinfo, and hop
  boundaries.
- Add a mutation-sensitive regression that checks cleanup timing while the
  raised error is still live.

## Implementation Units

### U1. Close rejected redirect errors before raising

**Files:** `scrape.py`

Construct the sanitized `HTTPError`, close it immediately, suppress only close
failures, and return it for the existing `raise self.rejected_redirect(...)`
call sites.

### U2. Add focused cleanup coverage

**Files:** `tests/test_scrape.py`

Add a fake redirect response with a close counter and assert that an unsafe
redirect increments it before the caught `HTTPError` escapes its handler frame.

### U3. Protect source, test, and docs contracts

**Files:** `scripts/check-docs-plans.py`, `README.md`, `SECURITY.md`,
`VISION.md`, `CHANGES.md`, `AGENTS.md`

Require the source cleanup fragments, focused test name, close assertion,
51-test README language, and guidance describing rejected redirect response body
cleanup.

## Scope Boundary

- Do not loosen the same-host redirect policy.
- Do not add live network tests or change allowed redirect targets.
- Do not change database, parser, body-size, content-type, or encoding
  behavior.
- Do not modernize beyond the existing Python 2/3-compatible style.

## Verification

- 51 tests passed under Python 3, including the focused rejected redirect
  response cleanup regression.
- make check PYTHON=python3 passed with documentation, syntax, 21 workflow
  mutations, and all offline tests.
- The redirect response cleanup mutation was rejected by the focused red test
  before the production fix.
- No `ResourceWarning` was emitted when the suite ran with Python warnings
  enabled.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.
