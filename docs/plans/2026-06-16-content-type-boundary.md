# Reject Explicit Non-HTML Scraper Responses

Status: Completed

## Context

The source fetch already bounds time, redirects, response bytes, and content
encoding. It still consumes and passes an explicitly non-HTML response to
BeautifulSoup, so a JSON, image, or binary endpoint can be silently treated as
an empty product page after unnecessary body reads.

## Priority

1. Reject declared non-HTML media types before the first body read.
2. Preserve compatibility with historical servers that omit `Content-Type`.
3. Keep validation offline, deterministic, and compatible with Python 2.7 and
   Python 3.12.

## Requirements

- Send an `Accept` header for HTML and XHTML source pages.
- Accept absent `Content-Type`, `text/html`, and `application/xhtml+xml`,
  including case and parameter variations.
- Reject every other declared media type, including conflicting duplicate
  declarations, before reading the response body.
- Close the response on every accepted or rejected path.
- Do not echo untrusted header values in errors or logs.
- Add dual-header-API runtime coverage and mutation-sensitive static contracts.
- Update contributor, security, vision, change, and completed-plan guidance.

## Intended Files

- `scrape.py`
- `tests/test_scrape.py`
- `scripts/check-docs-plans.py`
- `AGENTS.md`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-content-type-boundary.md`

## Work Completed

- Added a shared dual-runtime header reader and used it for content encoding and
  content type declarations across modern and legacy header APIs.
- Added an HTML/XHTML `Accept` request header and rejected explicit non-HTML
  media types before body reads without exposing header values.
- Preserved missing-header compatibility and response closure, including
  conflicting duplicate declaration coverage.
- Updated static contracts and project guidance for the new network boundary.

## Verification

- The pre-fix Python 3 reproduction consumed an explicit JSON response in two
  reads and returned `b'{}'` as parser input; the fixed tests reject it before
  the first read.
- 42 tests passed under Python 2.7 and Python 3.12.
- All 21 workflow mutations passed their fail-closed contract on both runtimes.
- Eight hostile content-type mutations were rejected on both runtimes: removed
  negotiation, rejected missing headers, allowed JSON, removed validation,
  removed pre-read proof, removed conflicting duplicates, removed guidance,
  and reopened plan status.
- The repository and external-directory `make check` passed under both runtimes
  after this completed evidence enabled the plan-aware static gate.
- Exact diff, generated-artifact and credential-pattern audits passed, along
  with conflict, mode, binary, file-size, and upstream relationship checks.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.

## Runtime Boundary

Validation uses offline response fakes and does not contact live retailers,
PostgreSQL, or credentialed services. The boundary verifies declared HTTP
metadata and parser input selection, not upstream correctness.
