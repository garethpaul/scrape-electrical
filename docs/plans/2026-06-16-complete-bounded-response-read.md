---
title: Complete Bounded Response Read
type: maintenance
status: completed
date: 2026-06-16
execution: code
---

# Complete Bounded Response Read

## Summary

Make `Product.read()` consume legal short reads until EOF or one byte beyond the
configured response limit, so fragmented responses are neither silently
truncated nor allowed to defer oversized data past the existing guard.

## Problem Frame

The response-size boundary currently calls `response.read(limit + 1)` once.
Python file-like objects may legally return fewer bytes than requested before
EOF. A fragmented response therefore returns only its first chunk, and bytes
remaining after that chunk are never parsed or counted against the configured
maximum.

## Requirements

- **R1:** Continue reading after nonempty short reads until EOF or until the
  accumulated body reaches `max_response_bytes + 1`.
- **R2:** Never request or retain more than one byte beyond the configured
  maximum.
- **R3:** Accept complete bodies exactly at the limit and reject complete or
  fragmented bodies above it before parsing.
- **R4:** Preserve response cleanup after success, oversize rejection, and read
  failure under Python 2.7 and Python 3.12.
- **R5:** Add focused tests and static contracts that reject regression to a
  single read, an unbounded read, missing remaining-byte accounting, missing
  EOF handling, or incomplete plan evidence.

## Scope Boundaries

- Do not change URL validation, redirect policy, timeout validation, parser
  selectors, database behavior, CLI options, dependencies, or hosted runtimes.
- Do not perform live HTTP, HTML parsing, database, credential, or deployment
  validation.
- Do not stream partial HTML into Beautiful Soup.

## Implementation Units

### U1. Accumulate Bounded Chunks

Read only the remaining allowance through `limit + 1`, append nonempty chunks,
stop on EOF, and join the response using the first chunk's text-or-byte type.
Retain the existing `finally` close boundary.

### U2. Protect Fragmented Response Semantics

Add dual-runtime tests for complete fragmented bodies, exact-limit bodies,
oversized fragmented bodies, bounded read sizes, and cleanup. Extend the docs
plan checker to require the loop, remaining-byte accounting, tests,
documentation, and completed evidence.

## Verification Plan

- Capture the pre-change short-read truncation reproduction.
- Run focused scraper tests under Python 2.7 and Python 3.12.
- Run repository and external-directory `make check` under both runtimes.
- Reject focused hostile implementation, test, documentation, and plan-status
  mutations.
- Run exact diff, generated-artifact, credential-pattern, and clean-worktree
  audits before shipping.

## Completion Evidence

Status: Completed

- Pre-change reproduction returned only the first `b'ab'` chunk instead of the
  complete `b'abcd'` body while still closing the response.
- 36 tests passed under Python 2.7 and Python 3.12.
- Both runtimes rejected single-read, dropped-remaining-accounting,
  first-chunk-only, unbounded-read, source-contract, test-contract,
  documentation-contract, and plan-status mutations. Sixteen focused hostile complete-read mutations were rejected.
- The repository and external-directory `make check` passed under both runtimes.
- The generated-artifact and credential-pattern audits passed for the intended
  diff.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.
