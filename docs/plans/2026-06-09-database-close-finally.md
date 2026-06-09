# Database Close Finally

## Status: Completed

## Context

`Database.close()` closed the cursor before the connection, but a cursor close
failure would still skip `conn.close()`. DB-API cleanup should attempt
connection teardown even when cursor cleanup fails.

## Objectives

- Preserve cursor-first close ordering.
- Ensure the connection close is attempted if cursor close raises.
- Cover the failure path with Python 2 unit tests and fake DB-API resources.
- Avoid changing insert or connection setup behavior.

## Work Completed

- Wrapped cursor close in `try/finally` so connection close still runs.
- Added a regression test with a cursor that records close order and raises.
- Updated README, VISION, and CHANGES notes for the connection cleanup guard.

## Verification

- `python2 -m py_compile scrape.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `git diff --check`
