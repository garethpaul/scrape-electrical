# Database Close Order

## Status: Completed

## Context

`Database.close()` closed the PostgreSQL connection before closing the cursor.
Closing cursors first is the safer lifecycle order for DB-API resources and
keeps cursor cleanup independent of connection teardown.

## Objectives

- Preserve existing insert and connection behavior.
- Close the cursor before closing the database connection.
- Add Python 2 regression coverage for cleanup order.
- Avoid requiring a live PostgreSQL server in tests.

## Work Completed

- Added fake cursor and connection classes that record close order.
- Added a regression test for cursor-first cleanup.
- Updated `Database.close()` to close `cur` before `conn`.
- Updated README, VISION, and CHANGES notes for the cleanup guard.

## Verification

- `python2 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
