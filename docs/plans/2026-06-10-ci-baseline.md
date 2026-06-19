# CI Baseline

Status: Completed

## Context

The repository has a legacy Python 2 scraper baseline behind `make check`.
Hosted validation must run the complete offline parser and database contract
instead of allowing an unavailable interpreter to turn tests into successful
skips.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Require Python 2 syntax, tests, documentation, and workflow contracts.
- Install no live scraping or database dependencies in hosted validation.
- Use least-privilege permissions and credential-free checkout.
- Pin the archived runtime image by digest and third-party actions by commit.
- Keep verification bytecode-free and independent of the caller's directory.

## Work Completed

- Added `.github/workflows/check.yml` for pull requests, pushes to `master`,
  and manual dispatches on a fixed Ubuntu 24.04 runner.
- Ran the full offline gate in the official Python 2.7.18 image pinned by
  digest without installing Beautiful Soup, psycopg2, or other live packages.
- Pinned checkout to the reviewed v6.0.3 commit, disabled persisted checkout
  credentials, and limited permissions to read-only repository contents.
- Made Python 2 mandatory for `make check` and removed successful skip paths.
- Anchored Makefile commands to the repository root.
- Added exact workflow-policy validation and hostile mutation coverage for
  triggers, credentials, actions, permissions, runner, timeout, image digest,
  failure handling, runtime proof, dependency installation, and commands.
- Updated README, VISION, SECURITY, CHANGES, and contributor guidance with the
  enforced hosted baseline.

## Verification

- `python2 -B scripts/test_workflow_contract.py`
- `make lint`
- `make contract-test`
- `make test`
- `make build`
- `make check`
- `docker run --rm -v "$PWD:/work:ro" -w /work python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20 make check`
- `git diff --check`

## Follow-Up Candidates

- Port the scraper implementation and tests to Python 3 or document the
  repository as Python 2 archive-only.
