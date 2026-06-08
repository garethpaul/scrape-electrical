# Parser Link Guard

## Status: Completed

## Context

`scrape-electrical` parses product cards and skips incomplete rows when titles
or prices are absent. A card with a title anchor but no usable `href` still
raised a `KeyError`, which could abort a scrape because a single malformed row
was not treated like the other incomplete product shapes.

## Objectives

- Preserve the Python 2 parser and mocked unit-test workflow.
- Skip product cards with missing or blank links.
- Cover missing-link and blank-link cards in unit tests.
- Preserve existing SQL, timeout, request-header, and docs-plan checks.

## Work Completed

- Added explicit missing and blank `href` handling in `Product.product_fields`.
- Extended parser tests for incomplete anchors.
- Updated README, VISION, and CHANGES notes for the parser guard.

## Verification

- `python2 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
