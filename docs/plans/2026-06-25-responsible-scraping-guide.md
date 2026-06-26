# Responsible Scraping Guide Plan

## Status: Completed

## Context

The roadmap required concrete target-site permission, request-rate, and data-
retention guidance. The README mentioned permission and rate limits but did not
define an approval record, distinguish robots rules from authorization, state
stop conditions, explain `Retry-After`, or provide deletion boundaries.

## Requirements

- Require explicit written permission with host, path, purpose, window, request
  budget, allowed fields, contact, storage, and retention scope.
- Require robots rules to be honored without presenting them as authorization.
- Keep live requests serial and prohibit broad scraping until tested pacing and
  backoff exist.
- Stop on blocks, instability, scope drift, exhausted budgets, and owner request.
- Honor `Retry-After` for `429` or `503` responses rather than immediately retry.
- Minimize retained fields, reject personal or account-only data collection, and
  define raw-response and derived-row deletion boundaries.
- Protect the guide, links, and completed roadmap state with the Python 2/3
  documentation contract.
- Keep the README offline-suite count synchronized with the 63 tests executed by
  the current gate.

## Files

- `RESPONSIBLE_USE.md`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `scripts/check-docs-plans.py`
- `CHANGES.md`
- `docs/plans/2026-06-25-responsible-scraping-guide.md`

## Scope Boundary

- Do not change network, retry, parser, database, CLI, dependency, or workflow
  behavior.
- Do not claim that robots rules, public availability, or this guide provide
  legal authorization.
- Do not perform live scraping or database writes during verification.

## Verification

- The documentation contract was added first and failed for the missing guide,
  links, required boundaries, plan, and stale roadmap item.
- The suite-count contract then failed on the stale README value before it was
  corrected from 51 to 63.
- Pinned Python 2.7 and local Python 3 `make check` passed all 63 offline tests,
  21 workflow mutations, documentation contracts, and Make authority gates.
- Thirteen hostile documentation mutations rejected removed permission, pacing,
  `Retry-After`, status, stop, retention, deletion, personal-data, link, roadmap,
  and suite-count boundaries.
- A retry mutation initially survived because the RFC URL contained the guarded
  phrase; excluding link targets from prose assertions fixed that false positive.
