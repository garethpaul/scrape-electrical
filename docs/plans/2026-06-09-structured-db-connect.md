# Structured Database Connection Parameters

## Status: Completed

## Context

`scrape-electrical` already parameterizes inserted product values and validates
table names, but `Database.__init__` still built the PostgreSQL connection
settings as one interpolated string. Operator-provided names, hosts, users, or
passwords should be handed to the database driver as structured fields instead
of being parsed from a single string.

## Objectives

- Preserve the existing PostgreSQL connection behavior.
- Pass database credentials and connection fields to `psycopg2` as keyword
  arguments.
- Cover the connection setup without requiring a live PostgreSQL server.
- Add the guard to the existing `make check` path.

## Work Completed

- Changed `Database.__init__` to call `psycopg2.connect` with `user`,
  `password`, `host`, and `dbname` keyword arguments.
- Added a Python 2 unit test with a mocked `psycopg2` module to verify the
  structured connection parameters.
- Extended `scripts/check-docs-plans.py` to reject interpolated psycopg2
  connection strings.
- Documented the connection-parameter guard in README, VISION, and CHANGES.

## Verification

- `python2 -m py_compile scrape.py`
- `python2 scripts/check-docs-plans.py`
- `python2 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add CLI parsing for database settings and a dry-run mode before live use.
- Add explicit connection error handling around `Database` initialization.
