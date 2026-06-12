# CI Baseline

Status: Completed

## Context

The repository had local Python 2 verification for the legacy scraper and a
Python-compatible docs-plan guard, but no hosted workflow ran a baseline for
pushes and pull requests. Hosted runners do not provide Python 2 by default, so
the CI path needs to be explicit about what it can verify.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Updated `make check` so it still runs Python 2 compile/tests when `python2`
  is available, and otherwise runs the documentation-plan baseline with
  Python 3.
- Extended the docs-plan checker and docs so the hosted CI path stays visible.

## Verification

- `make check`
