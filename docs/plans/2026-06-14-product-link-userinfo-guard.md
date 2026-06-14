# Product Link Userinfo Guard

## Status: Completed

## Context

The scraper rejects credentials in its operator-supplied source URL and in
redirect targets, but `Product.normalized_link()` still accepts usernames and
passwords embedded in product links parsed from remote HTML. Those values can
therefore be persisted to PostgreSQL or emitted by `--dry-run`.

## Priority

High data-boundary integrity. Product links identify public web resources;
remote markup must not turn the scraper into a credential storage or disclosure
path.

## Requirements

- Reject parsed HTTP(S) product links containing a username or password.
- Skip credential-bearing links without echoing their values or aborting the
  remaining product scrape.
- Preserve credential-free absolute and relative HTTP(S) links.
- Add Python 2 regression coverage and fail-closed static contracts.
- Keep maintained documentation and completed verification evidence aligned.

## Scope Boundaries

- Do not change source URL, redirect, DNS, product-host, database, parser,
  dependency, or Python 2 compatibility policy.

## Verification

- focused Python 2 product-link userinfo regression
- repository and external-directory `make check`
- digest-pinned, network-disabled Python 2.7.18 container `make check`
- hostile guard, test, documentation, suite-count, and plan-status mutations
- Python bytecode, generated-artifact, credential-pattern, and exact-diff audits

## Verification Results

- The focused Python 2 regression passed and confirmed credential-bearing
  product links are skipped while a following safe product is still inserted.
- The repository and external-directory `make check` passed with all 31
  dependency-free tests and all 17 workflow-policy mutations.
- The reviewed digest-pinned Python 2.7.18 container passed `make check` with a
  read-only checkout and networking disabled.
- Six hostile product-link userinfo mutations were rejected across guard
  removal, password-only weakening, test removal, documentation drift,
  suite-count drift, and completed-plan status.
- Final Python bytecode, generated-artifact and credential-pattern audits passed
  with only the intended parser, test, checker, documentation, and plan changes.
