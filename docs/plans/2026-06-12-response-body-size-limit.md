# Response Body Size Limit

## Status: Completed

## Context

`Product.read()` applies a network timeout and closes responses, but it calls
`response.read()` without a size. A permitted endpoint can therefore return an
arbitrarily large body and exhaust process memory before BeautifulSoup parses
the page.

## Priority

The scraper should bound both network duration and response memory while
remaining compatible with Python 2.7 and the dependency-free offline tests.

## Requirements

- R1. Define a conservative default maximum response size.
- R2. Read at most one byte beyond the configured maximum and reject oversized
  bodies before parsing.
- R3. Accept bodies exactly at the configured boundary.
- R4. Close responses after successful, failed, and oversized reads.
- R5. Reject non-positive maximum values.
- R6. Expose and forward `--max-response-bytes` through the CLI and `main()`.
- R7. Protect implementation, tests, docs, and completed plan with focused
  hostile mutations and `make check`.

## Scope Boundaries

- Do not change parser selectors, database writes, timeout behavior, or links.
- Do not stream partial HTML into BeautifulSoup.
- Do not add dependencies or modernize away from Python 2 in this change.

## Verification Plan

- focused failing tests before implementation
- `python2 -B -m unittest discover -s tests`
- `make check`
- digest-pinned Python 2.7 container verification
- focused hostile response-limit mutations
- `git diff --check`

## Work Completed

- Added a 5 MiB default maximum and positive-integer constructor validation.
- Read exactly one byte beyond the configured maximum, accepted exact-boundary
  bodies, rejected oversized bodies before parsing, and retained `finally`
  response cleanup for every outcome.
- Added `--max-response-bytes` and forwarded it through `run_cli()`, `main()`,
  and `Product` without changing timeout or database behavior.
- Expanded the Python 2 suite to 25 tests and protected implementation, tests,
  docs, and completed status through the docs-plan checker.

## Verification

- The focused tests failed on the unbounded implementation before code changes.
- `python2 -B -m unittest discover -s tests` passed 25 tests.
- `make check` passed locally and in the digest-pinned Python 2.7 container.
- 10 focused hostile response-limit mutations were rejected with valid Git
  metadata.
- No Python bytecode or generated artifacts were left in the checkout, and
  `git diff --check` passed.
