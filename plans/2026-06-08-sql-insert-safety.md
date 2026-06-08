# SQL Insert Safety

## Problem

The scraper imported missing modules at load time and built SQL insert values by
string concatenation. That made the script hard to test and unsafe for
user-provided product fields.

## TDD Evidence

1. Added mocked Python 2 unit tests for `Database.insert`.
2. Ran `make test` before source fixes and confirmed import failed on the
   missing `lib` module.
3. Removed the unused import, moved optional dependencies to their call sites,
   parameterized insert values, validated table names, and reran the gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
