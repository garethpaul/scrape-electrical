# Make Root Override Protection

## Status: Completed

## Context

The Makefile derives its repository root from the loaded file and uses that
path for Python 2 documentation, workflow, syntax, and offline behavior gates.
GNU Make command-line variables outrank an ordinary assignment, so `make
ROOT=/tmp check` can redirect those commands away from the checkout.

## Requirements

- **R1:** Prevent command-line and environment values from replacing the
  Makefile-derived repository root.
- **R2:** Keep the `PYTHON` interpreter configurable.
- **R3:** Require the exact protected declaration in the Python 2 checker.
- **R4:** Prove every public Make alias from the checkout and an external
  directory with a hostile `ROOT` argument.
- **R5:** Preserve URL validation, redirect bounds, response cleanup, database
  safety, workflow policy, and bytecode-free verification.

## Implementation Units

### U1. Protected Root

Give the repository-derived root override precedence without changing recipes
or runtime selection.

### U2. Offline Contract

Extend `scripts/check-docs-plans.py` to reject weakened, duplicate, displaced,
or caller-controlled root declarations and incomplete evidence.

### U3. Verification

Run documentation, workflow, syntax, offline tests, all Make aliases, the
digest-pinned Python 2 image, hostile mutations, and integrity screening.

## Scope Boundary

- Do not modify scraper, database, parser, redirect, or response behavior.
- Do not change workflow policy, Python runtime, or dependency installation.
- Do not add credentials, bytecode, caches, or generated outputs.

## Verification

- `python2 -B scripts/check-docs-plans.py`
- `make check`
- external `make ROOT=/tmp check`
- root-declaration, checker, plan-status, README-index, and evidence mutations
- Python syntax, workflow contract, protected-file, secret, artifact, and
  `git diff --check` gates

## Work Completed

- Protected the Makefile-derived repository root from command-line and
  environment overrides while preserving configurable Python selection.
- Added Python 2-compatible exact declaration, completed-evidence, and README
  index contracts.
- Preserved scraper, database, redirect, response, workflow, and bytecode-free
  behavior boundaries.

## Verification Results

- `python2 -B scripts/check-docs-plans.py` passed.
- From both the checkout and an external directory, all six public Make aliases passed.
- `make ROOT=/tmp check` passed externally while still executing repository-owned
  documentation, workflow, syntax, and offline behavior gates.
- The digest-pinned Python 2.7.18 hosted image passed `make check` with
  networking disabled and the source mounted read-only.
- Six hostile mutations were rejected across root declaration, checker
  expectation, plan status, README indexing, and recorded evidence.
- Python syntax, workflow contract, exact-base protected-file comparison,
  secret screening, bytecode/generated-artifact screening, and
  `git diff --check` passed before shipping.
