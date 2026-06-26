---
title: Non-String URL Guard
type: fix
status: completed
date: 2026-06-25
---

# Non-String URL Guard

## Status: Completed

## Problem

Truthy non-string source URLs and parsed product `href` values reached
`.strip()`, raising `AttributeError`. A malformed parser value could therefore
abort the entire scrape instead of being rejected or skipped safely.

## Decision

Use one Python 2/3-compatible string type tuple before URL normalization.
Non-string source URLs raise the existing sanitized `ValueError`; non-string
product links return `None` so the scraper continues with later rows.

## Verification Completed

- Covered `None`, booleans, integers, lists, and arbitrary objects for source
  and product-link inputs.
- Verified source failures do not echo caller values.
- Ran `make check PYTHON=python3`; Python 2 was unavailable locally, so the
  hosted Python 2.7 gate remains the required second-runtime verification.
