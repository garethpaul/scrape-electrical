# Malformed Product Link Boundary

## Status: Planned

## Context

`Product.normalized_link()` validates product-link schemes and credentials, but
malformed authorities can still make URL parsing or hostname inspection raise
`ValueError`. Because product links come from remote markup, one malformed row
must not abort processing of later safe products.

## Priority

High parser-boundary resilience. Untrusted product metadata should be rejected
at the row boundary without interrupting the rest of an offline or live scrape.

## Requirements

- Treat malformed absolute or relative product-link authorities as invalid.
- Skip only the malformed row and continue processing later safe products.
- Preserve existing credential-free absolute and relative HTTP(S) links.
- Add Python 2 regression coverage and a fail-closed static contract.
- Keep maintained documentation, suite counts, and verification evidence aligned.

## Scope Boundaries

- Do not change source URL, redirect, DNS, product-host, database, dependency,
  response-size, or Python 2 compatibility policy.
- Do not log or echo rejected link values.

## Implementation Units

1. Contain URL parsing and hostname failures in `Product.normalized_link()`.
2. Add a regression proving malformed links are skipped and later safe rows are
   still inserted.
3. Extend the plan checker and maintained documentation with the parser boundary
   and completed verification evidence.

## Verification

- focused Python 2 malformed-link regression
- repository and external-directory `make check`
- digest-pinned, network-disabled Python 2.7.18 container `make check`
- hostile guard, test, documentation, suite-count, and plan-status mutations
- Python bytecode, generated-artifact, credential-pattern, and exact-diff audits

## Risks

- Python 2 `urlparse` behavior differs from current Python releases, so the
  maintained Python 2 runtime remains the authoritative compatibility gate.
- Validation remains offline and does not exercise production source HTML,
  PostgreSQL, DNS, or live network behavior.
