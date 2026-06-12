# HTTP Response Cleanup

## Status: Completed

## Context

`Product.read()` read the `urllib2` response body without closing the response.
Repeated scraper runs could therefore retain sockets, especially when body
reads raised before returning content.

## Objectives

- Close source-page responses after successful reads.
- Close source-page responses when body reads fail.
- Preserve request URL and timeout behavior.

## Work Completed

- Wrapped response body reads in a `finally` cleanup block.
- Added Python 2 tests for successful and failing response reads.
- Updated README, SECURITY, VISION, and CHANGES guidance.

## Verification

- `python2 -B -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
