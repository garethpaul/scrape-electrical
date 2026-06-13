# Redirect Hop Limit

## Status: Completed

## Context

The same-host redirect handler validated each target but inherited Python 2's
implicit redirect budgets. Long same-host chains and loops therefore depended
on legacy library defaults that were not visible in the scraper contract.

## Priority

Redirect target validation and redirect depth are separate network safety
boundaries. The scraper should fail after a small, reviewed number of hops even
when every individual target remains on the approved host.

## Objectives

- Limit a request chain to five total redirects.
- Limit repeated visits to the same redirect target to two.
- Preserve same-host, port, credential, scheme, and HTTPS-upgrade rules.
- Add Python 2 regression and fail-closed documentation contracts.
- Keep the offline test gate free of live network and database dependencies.

## Work Completed

- Declared explicit `max_redirections` and `max_repeats` values on the custom
  Python 2 redirect handler.
- Added an offline unit test for both budgets.
- Extended the plan checker and project guidance with the redirect hop limit.

## Verification

- `python2 -B -m unittest tests.test_scrape`
- `make check` locally and from outside the repository root
- digest-pinned, read-only, network-isolated Python 2.7.18 gate
- focused hop, repeat, test, documentation, and plan mutations
- Python 2 syntax, workflow YAML, bytecode, secret, artifact, and
  `git diff --check` audits

The focused discovery run and full `make check` passed all 29 offline Python 2
tests. Local and root-independent gates also passed documentation contracts,
Python 2 syntax, and all 17 workflow-policy mutations. The exact digest-pinned
Python 2.7.18 image passed the same gate with a read-only checkout and disabled
networking.

All five focused repeat-budget, hop-budget, missing-test, documentation, and
plan-status mutations were rejected. Bytecode, generated-artifact,
high-confidence secret, and `git diff --check` audits passed.

## Scope Boundary

This bounds redirect depth but does not resolve DNS rebinding, decompression
expansion, parser CPU limits, live-site compatibility, or Python 2 obsolescence.
