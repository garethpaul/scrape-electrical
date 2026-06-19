# Hosted Python 2 Scraper Validation

Status: Completed

## Context

The initial GitHub Actions baseline used Python 3.12 only. The canonical gate
therefore ran the documentation checker but reported success after skipping the
Python 2 scraper syntax check and all 19 unit tests. The offline suite uses
mocks and fixtures, so it does not need Beautiful Soup, psycopg2, network
access, or a PostgreSQL service.

## Objectives

- Run every offline scraper test on the required Python 2.7 runtime.
- Remove successful skip paths from the canonical gate.
- Install no live scraping or database dependencies in hosted validation.
- Pin the runtime image by digest and actions by immutable commit.
- Keep `make check` independent of the caller's working directory.

## Work Completed

- Changed CI to the official Python 2.7.18 image pinned by digest.
- Pinned checkout to the reviewed v6.0.3 commit on Ubuntu 24.04.
- Disabled persisted checkout credentials and limited permissions to read-only
  repository contents.
- Made Python 2 syntax and all 19 tests mandatory for `make check`.
- Removed setup-python and all unavailable-runtime success paths.
- Anchored Makefile commands to the repository root.
- Extended the checker to enforce the exact runtime, action, credential,
  permission, command, no-dependency, and no-skip contracts.
- Added hostile mutation tests for duplicate, relocated, or contradictory
  credentials and other workflow-policy drift.

## Verification

- `python2 -B scripts/test_workflow_contract.py`
- `make contract-test`
- `docker run --rm -v "$PWD:/work:ro" -w /work python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20 make check`
- `git diff --check`
