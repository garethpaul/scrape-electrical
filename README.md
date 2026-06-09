# scrape-electrical

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/scrape-electrical` is a public sample, documentation, or utility project. Personal scrape for * electrical with a given URL

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `CHANGES.md` - maintenance history for scraper safety checks
- `Makefile` - local verification entry points
- `docs/plans` - completed maintenance plans for the current baseline
- `plans` - historical implementation notes
- `requirements.txt` - optional scraper/database dependencies
- `scripts` - documentation-plan validators
- `scrape.py` - scraper and PostgreSQL insert implementation
- `tests` - Python 2 parser and database unit tests
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: requirements.txt
- Entry points or build surfaces: none detected
- Test-looking files: tests/test_scrape.py

## Getting Started

### Prerequisites

- Git
- Python 2.7
- PostgreSQL client access for live database writes

### Setup

```bash
git clone https://github.com/garethpaul/scrape-electrical.git
cd scrape-electrical
python2 -m pip install -r requirements.txt
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Import `scrape.py` from a small driver that creates a `Database` instance and
  passes it to `main(database, url)`.
- Confirm target-site permission and rate limits before scraping.
- Use test data first; the script writes to PostgreSQL when `Product.find()`
  inserts parsed products.
- The default request path does not set fake browser, referer, or randomized
  tracking headers.
- Live fetches use a bounded default timeout so stalled requests do not hang
  forever.
- Product cards without usable links are skipped rather than aborting the
  scrape.
- Database connection fields are passed to `psycopg2` as structured keyword
  arguments instead of an interpolated connection string.

## Testing and Verification

- `make check` runs Python 2 syntax checks plus mocked database and parser
  unit tests.
- Parser tests cover missing prices, missing titles, and missing or blank
  product links.
- Database tests cover parameterized inserts and structured `psycopg2`
  connection parameters without requiring a live PostgreSQL server.
- Database tests also cover cursor-first cleanup before connection close.
- `make check` also requires completed canonical plans under `docs/plans`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include scrape.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include scrape.py.
- Review changes touching database, model, or persistence code; examples from the scan include scrape.py.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-scrape-electrical-baseline.md` for the canonical
  scraper/database safety baseline.
- See `docs/plans/2026-06-08-network-timeout.md` for the network timeout
  guard.
- See `docs/plans/2026-06-08-parser-link-guard.md` for incomplete product-link
  handling.
- See `docs/plans/2026-06-09-structured-db-connect.md` for structured
  database connection parameters.
- See `docs/plans/2026-06-09-database-close-order.md` for cursor-first
  database cleanup coverage.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
