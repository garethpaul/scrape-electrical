# Source URL Scheme Guard

## Status: Completed

## Context

The scraper already normalized product links and rejected non-web product hrefs,
but the source page URL itself was accepted as provided. A `file:`, `javascript:`,
blank, or hostless source URL could reach `urllib2` before any scraper boundary
checked it.

## Objectives

- Accept only `http` and `https` source page URLs with a host.
- Trim harmless surrounding whitespace from source URLs.
- Reject blank, local-file, script, and hostless source URLs before network
  reads.
- Preserve relative product-link normalization against the validated source URL.

## Work Completed

- Added `Product.normalized_source_url()` and call it during construction.
- Added Python 2 tests for invalid source URL schemes and whitespace trimming.
- Extended `scripts/check-docs-plans.py` to preserve source URL validation and
  security-policy documentation.
- Updated README, SECURITY, VISION, and CHANGES notes for the source URL guard.

## Verification

- Negative: `python2 -m unittest discover -s tests` failed before the fix
  because non-web source URLs were accepted and whitespace was preserved.
- `python2 -m unittest discover -s tests`
- `python2 -m py_compile scrape.py`
- `python2 scripts/check-docs-plans.py`
- `make lint`
- `make check`
- `make verify`
- `git diff --check`
