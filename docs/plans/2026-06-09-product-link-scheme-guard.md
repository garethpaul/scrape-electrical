# Product Link Scheme Guard

## Status: Completed

## Context

`Product.product_fields()` checked that scraped product links existed, but it
accepted any href string. Malformed or hostile markup could insert
`javascript:`, `file:`, or other non-web links into the database, and relative
links were stored without enough context to revisit the product later.

## Objectives

- Preserve existing product parsing for complete product cards.
- Resolve relative product links against the source page URL.
- Insert only `http` and `https` product links.
- Skip non-web link schemes instead of aborting the scrape.
- Add Python 2 regression coverage and static checks for the link guard.

## Work Completed

- Added `Product.normalized_link()` using Python 2 `urljoin` and `urlparse`.
- Updated `Product.product_fields()` to skip links that cannot be normalized to
  HTTP(S).
- Added tests for rejecting `javascript:`, `file:`, and `mailto:` links.
- Added tests for normalizing relative product links against the source URL.
- Extended `scripts/check-docs-plans.py` to preserve the URL normalization
  guard.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: `python2 -m unittest discover -s tests` failed before the parser
  fix because unsafe schemes were inserted and relative links stayed relative.
- `python2 -m unittest discover -s tests`
- `python2 -m py_compile scrape.py`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `make verify`
- `git diff --check`
