# Source URL Userinfo Guard

## Status: Planned

## Context

Redirect targets already reject embedded usernames and passwords, but
`Product.normalized_source_url()` still accepts userinfo in the
operator-supplied source URL. A URL such as
`https://user:password@example.test/products` can therefore carry credentials
into the initial request before the redirect boundary applies.

## Priority

Scraper source URLs identify content, not an authentication transport. Rejecting
userinfo before network access avoids accidental credential disclosure through
request URLs, diagnostics, proxies, or copied command history while preserving
ordinary credential-free HTTP(S) sources.

## Objectives

- Reject source URLs containing a username or password before building an
  opener or request.
- Preserve credential-free HTTP and HTTPS source URLs, including relative
  product-link normalization and existing redirect behavior.
- Add dependency-free Python 2 regression coverage for username-only,
  password-bearing, and percent-encoded userinfo cases.
- Protect the boundary with fail-closed static and documentation contracts.

## Implementation Units

### U1. Reject source userinfo

**Files:** `scrape.py`, `tests/test_scrape.py`

Validate parsed source URL userinfo alongside the existing scheme and host
checks. Exercise representative credential-bearing authorities and confirm
rejection happens during `Product` construction.

### U2. Preserve the contract

**Files:** `scripts/check-docs-plans.py`, `README.md`, `VISION.md`,
`SECURITY.md`, `CHANGES.md`

Require the source credential boundary in code and maintained guidance, then
add focused hostile mutations for guard, tests, documentation, and plan status.

## Verification

- Focused Python 2 unit tests for source URL validation.
- Full `make check` locally, outside the repository root, and in the reviewed
  digest-pinned Python 2.7.18 container with networking disabled.
- Focused hostile mutations plus Python syntax, workflow YAML, bytecode,
  generated-artifact, secret, and `git diff --check` audits.

## Scope Boundary

This change does not add authenticated scraping, resolve DNS rebinding, change
redirect policy, alter product-link host handling, or modernize Python 2.
