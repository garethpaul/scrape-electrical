# Make Authority Isolation

## Status: Completed

## Context

The protected repository root stopped direct `ROOT=/tmp` redirection, but GNU
Make still accepted caller-controlled preload files, file lists, recipe shells,
Python commands, and bytecode settings. Python selection must remain available
because CI intentionally verifies the offline suite on both Python 2 and 3.

## Requirements

- **R1:** Load the repository Makefile alone and reject overridden file lists.
- **R2:** Derive the checkout root safely from the exact Makefile path.
- **R3:** Permit exactly `python2` or `python3` without expanding Make functions.
- **R4:** Keep shell execution and bytecode suppression repository-owned.
- **R5:** Exercise every public target across both supported runtimes and
  hostile authority inputs.

## Implementation

- Hardened Make authority during parsing and again after the final Makefile set
  is known, before any public target can run.
- Added a dual-runtime `root-test` checkout with spaces, quotes, and
  command-substitution syntax in its path.
- Covered seven public targets across eleven successful authority modes and 21
  rejected runtime, function, file-list, preload, and multi-Makefile cases.
- Left scraper, parser, network, database, workflow, and dependency behavior
  unchanged.

## Verification

- `make root-test` passed 77 target/authority cases and 21 rejection cases,
  including extra `-f` inputs before and after the repository Makefile.
- `make check PYTHON=python2` and `make check PYTHON=python3` passed from the
  repository and through an absolute Makefile path.
- Python and shell syntax checks, bytecode screening, `git diff --check`, and
  repository integrity screening passed.
