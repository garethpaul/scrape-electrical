# Malformed Source URL Boundary

## Status: Completed

## Context

`Product.normalized_source_url()` validates the source scheme, authority, and
hostname, but it does not access Python 2's parsed `port` property. A source URL
with a malformed port can therefore pass construction and fail later while the
redirect handler is being built.

## Priority

High input-boundary resilience. Invalid source authorities should fail before
network setup, with the same non-disclosing error used for other malformed
source URLs.

## Requirements

- Parse and validate the source port during source URL normalization.
- Reject malformed IPv6 authorities and nonnumeric or out-of-range ports before
  `urllib2` opener construction.
- Do not echo rejected source URLs or embedded input in error messages.
- Preserve valid HTTP(S) source URLs, explicit ports, credential rejection,
  redirect policy, response limits, and Python 2 compatibility.
- Add focused regression coverage and a fail-closed documentation contract.

## Scope Boundaries

- Do not change DNS, redirect, product-link, PostgreSQL, dependency, or live
  network behavior.
- Do not add Python 3-only syntax or packages.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation Units

1. Force source-port validation inside `normalized_source_url()` and keep the
   generic non-disclosing malformed-source error.
2. Add Python 2 tests for malformed ports and valid explicit ports.
3. Extend the plan checker and maintained documentation with mutation-sensitive
   source-authority evidence.

## Verification

- focused Python 2 source-authority regression
- repository and external-directory `make check`
- digest-pinned, network-disabled Python 2.7.18 container `make check`
- hostile source-port, test, documentation, suite-count, and plan-status
  mutations
- Python bytecode, generated-artifact, credential-pattern, and exact-diff audits

## Verification Results

- The focused Python 2 regression passed for nonnumeric, empty, out-of-range,
  malformed IPv6, and valid explicit source ports.
- The repository and external-directory `make check` passed with all 33 offline
  scraper tests and all 17 workflow-policy mutations.
- The digest-pinned, network-disabled Python 2.7.18 container passed the full
  read-only `make check` gate.
- Seven hostile malformed-source mutations were rejected across source-port
  parsing, explicit-port detection, empty-host validation, regression coverage,
  documentation, suite count, and completed-plan evidence.
- Final Python bytecode, generated-artifact and credential-pattern audits passed
  with only the intended parser, test, checker, documentation, and plan changes.

## Remaining Risks

- Python 2.7 remains end-of-life and its URL parser is the authoritative runtime
  for this constrained legacy scraper.
- Validation remains offline and does not exercise production source pages,
  DNS behavior, PostgreSQL, or live redirects.
