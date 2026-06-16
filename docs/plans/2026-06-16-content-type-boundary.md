# Reject Explicit Non-HTML Scraper Responses

Status: Planned

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

## Verification Planned

- Reproduce the pre-fix read of an explicit JSON response.
- Run focused response tests and complete repository/external-directory gates
  on Python 2.7 and Python 3.12.
- Reject isolated implementation, test, documentation, and plan mutations.
- Audit the exact diff, generated artifacts, credentials, conflicts, modes,
  binaries, file sizes, and upstream relationship before commit.

## Runtime Boundary

Validation uses offline response fakes and does not contact live retailers,
PostgreSQL, or credentialed services. The boundary verifies declared HTTP
metadata and parser input selection, not upstream correctness.
