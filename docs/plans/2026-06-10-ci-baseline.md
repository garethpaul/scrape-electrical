# CI Baseline

Status: Completed

## Context

The repository had local Python 2 verification for the legacy scraper and a
Python-compatible docs-plan guard, but no hosted workflow ran a baseline for
pushes and pull requests. Hosted runners do not provide Python 2 by default,
so CI must still enforce repository contracts without presenting legacy parser
and database behavior as tested.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check` with pinned Node 24-compatible actions.
- Made the Python 3 documentation-plan guard unconditional.
- Kept Python 2 compile and unit tests active when `python2` is installed, with
  explicit skips limited to those legacy steps otherwise.
- Restricted workflow permissions to read-only contents and bounded the job to
  five minutes.
- Extended the docs-plan checker and docs so the hosted CI path stays visible.

## Verification

- `python3 -B scripts/check-docs-plans.py`
- `make check`
- `make check PYTHON=python2-unavailable`
- `git diff --check`

## Superseded Limitation

The successful Python 2 skip behavior described above was replaced on
2026-06-10 by the full offline runtime gate in
`docs/plans/2026-06-10-hosted-legacy-validation.md`.
