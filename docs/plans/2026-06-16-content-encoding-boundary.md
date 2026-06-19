---
title: Reject Compressed Scraper Responses
type: security
status: completed
date: 2026-06-16
execution: code
---

# Reject Compressed Scraper Responses

## Summary

Make the scraper request an identity representation and reject any response
that declares a non-identity `Content-Encoding` before body reads, so the
existing byte cap unambiguously bounds the exact bytes passed to the HTML
parser.

## Problem Frame

`Product.read()` bounds application-level response bytes, but the request does
not state an encoding preference and the response encoding is not validated.
The standard-library opener does not provide a reviewed decompression boundary.
Accepting compressed representations would make parser input and expansion
behavior dependent on transport or future adapter changes rather than the
configured `max_response_bytes` contract.

## Requirements

- **R1:** Add `Accept-Encoding: identity` to source-page requests without
  changing the source URL or redirect policy.
- **R2:** Accept an absent, blank, or case-insensitive `identity`
  `Content-Encoding` value.
- **R3:** Reject every other declared content encoding before the first body
  read and without echoing the untrusted header value.
- **R4:** Close the response after success, encoding rejection, oversize
  rejection, or read failure under Python 2.7 and Python 3.12.
- **R5:** Preserve complete bounded reads, exact-limit acceptance, redirect
  controls, timeout validation, parser selectors, database behavior, CLI
  options, dependencies, and hosted runtime coverage.
- **R6:** Add focused executable and static contracts that reject removal of
  the request header, response check, pre-read ordering, cleanup, guidance, or
  completed-plan evidence.

## Scope Boundaries

- Do not add gzip, deflate, or Brotli decompression.
- Do not inspect or trust compressed `Content-Length` as a parser-input bound.
- Do not perform live HTTP, HTML parsing, PostgreSQL, credential, or deployment
  validation.
- Do not change the existing `--max-response-bytes` meaning or default.

## Implementation Units

### U1. Declare And Enforce Identity Encoding

Set the request header in `Product.build_request()`. Add a small response-header
helper that works with Python 2 and Python 3 response metadata, normalizes the
declared value, and rejects non-identity encodings before `response.read()`.

### U2. Protect The Boundary

Extend offline response fakes and dual-runtime tests for request headers,
accepted identity variants, compressed-response rejection before reads, generic
errors, and response cleanup. Extend the static baseline and synchronized
guidance with completed plan evidence.

## Verification Plan

- Capture the pre-change reproduction showing no `Accept-Encoding` request
  header and a gzip-declared body reaching the bounded read.
- Run focused scraper tests under Python 2.7 and Python 3.12.
- Run repository and external-directory `make check` under both runtimes.
- Reject hostile source, test, documentation, and plan-status mutations.
- Audit the exact diff, Python syntax, generated artifacts, dependency drift,
  credential patterns, conflict markers, modes, and whitespace before shipping.

## Risks

- Some live sites may require compressed transfer; this archive scraper will
  fail closed instead of adding an unbounded decompression path.
- Header APIs differ between Python 2 and Python 3, so tests must exercise both
  supported runtime lanes.
- PR #16 will be stacked on open PR #15 and requires base-first ordering;
  neither pull request may be merged or closed without explicit authorization.

## Completion Evidence

Status: Completed

- The pre-change reproduction showed no `Accept-Encoding` request header and a
  gzip-declared response reaching two body reads.
- 39 tests passed under Python 2.7 and Python 3.12.
- repository and external-directory `make check` passed under both runtimes.
- hostile content-encoding mutations were rejected.
- generated-artifact and credential-pattern audits passed.
- No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised.
