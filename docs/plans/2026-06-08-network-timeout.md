# Network Timeout Guard

## Status: Completed

## Context

`Product.read()` opens the target URL before parsing product rows. Without an
explicit timeout, a stalled network request can hang the scraper indefinitely
and leave operators uncertain whether database writes are still pending.

## Objectives

- Keep request construction free of spoofing headers.
- Add a bounded default timeout for live fetches.
- Reject invalid non-positive timeout values.
- Cover the behavior without making live network requests.

## Work Completed

- Added a default 30-second timeout to `Product`.
- Passed the timeout through `urllib2` opener calls in `Product.read()`.
- Added Python 2 unit tests for timeout propagation and invalid timeout values.
- Updated README, VISION, and CHANGES.

## Verification

- `python2 -m py_compile scrape.py`
- `python2 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add CLI argument parsing so timeout, dry-run, and database settings can be
  passed explicitly.
- Add retry/backoff behavior only after documenting target-site permission and
  rate limits.
