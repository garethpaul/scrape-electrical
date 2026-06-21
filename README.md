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
- `tests` - Python 2 and Python 3 parser and database unit tests
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
- Python 2.7 or Python 3.12 for offline verification
- PostgreSQL client access for live database writes

### Setup

```bash
git clone https://github.com/garethpaul/scrape-electrical.git
cd scrape-electrical
python3 -m pip install -r requirements.txt
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Preview parsed rows without PostgreSQL writes:

```bash
python3 scrape.py --url https://example.test/products --dry-run
```

- For live writes, pass all database fields explicitly:

```bash
python3 scrape.py --url https://example.test/products \
  --db-name products_db \
  --db-user scraper \
  --db-password "$SCRAPE_DB_PASSWORD" \
  --db-host db.example.test \
  --table-name products
```

- Existing callers can still import `scrape.py`, create a `Database` instance,
  and pass it to `main(database, url)`.
- Confirm target-site permission and rate limits before scraping.
- Use test data first; the script writes to PostgreSQL when `Product.find()`
  inserts parsed products.
- Use `--dry-run` before live writes to confirm parser output.
- The default request path does not set fake browser, referer, or randomized
  tracking headers.
- Live fetches use a bounded default timeout so stalled requests do not hang
  forever.
- Scraper timeouts must be finite positive numbers before network setup.
- Live fetches also enforce a 5 MiB response body size limit before HTML
  parsing; override it with `--max-response-bytes` for a reviewed target. The
  bounded response reads consume short chunks through EOF so fragmented
  bodies cannot be silently truncated or escape the size check.
- Source requests require identity content encoding, and responses that declare
  any other content encoding are rejected before body reads.
- Source requests advertise HTML and reject explicit non-HTML content types
  before body reads; missing `Content-Type` remains accepted for legacy sites.
- Source page URLs must use `http` or `https` and include a host before the
  scraper opens them; malformed source URL authorities are rejected before
  opener construction.
- Embedded source URL credentials are rejected before the scraper builds a
  request.
- Source-page redirects use a same-host redirect boundary: relative paths and
  same-host HTTPS upgrades are allowed, while cross-host, non-web, hostless,
  alternate-port, downgrade, and credential-bearing targets are rejected before
  the follow-up request.
- Rejected redirect response bodies are closed before the sanitized redirect
  error is raised, so blocked redirects do not leak response resources.
- The redirect hop limit permits at most five total redirects and two repeats
  of the same target before the runtime aborts the request chain.
- Product cards without usable links are skipped rather than aborting the
  scrape.
- Parsed product links are resolved against the source URL, must use `http` or
  `https`, must not contain product link credentials, and malformed product
  links are skipped before insertion without stopping later safe rows.
- Database connection fields are passed to `psycopg2` as structured keyword
  arguments instead of an interpolated connection string.

## Testing and Verification

- `make check PYTHON=python2` and `make check PYTHON=python3` run syntax checks
  plus all 51 mocked database and parser tests under Python 2.7 and Python 3.12.
- Both gates run documentation and workflow-policy checks without successful
  skip paths or live scraper/database dependencies.
- GitHub Actions runs the same offline gate in a digest-pinned Python 2.7.18
  container and an Ubuntu Python 3.12 lane, with credential-free pinned
  checkout and read-only permissions.
- Parser tests cover missing prices, missing titles, and missing or blank
  product links.
- Parser tests also cover non-web, credential-bearing, and malformed product
  links plus relative product-link normalization and continuation after
  rejected rows.
- Parser tests also cover source page URL scheme, malformed authority, explicit
  port, and whitespace normalization.
- Network tests require HTTP responses to close after successful and failed
  body reads.
- Network tests require rejected redirect response bodies to close before the
  sanitized redirect error escapes.
- Network tests cover the exact response body size limit, oversized rejection,
  configured read size, and response closure.
- Network tests cover HTML/XHTML response declarations, missing legacy media
  types, and pre-read rejection of explicit non-HTML content types.
- Redirect tests lock the five-hop and two-repeat budgets.
- Database tests cover parameterized inserts and structured `psycopg2`
  connection parameters without requiring a live PostgreSQL server.
- Database tests also cover cursor-first cleanup, connection close attempts
  when cursor cleanup fails, connection cleanup when cursor construction fails,
  primary-error preservation when that cleanup also fails, and cleanup when
  product validation rejects input after database creation.
- Product construction primary error preservation keeps validation and
  interruption failures authoritative when database cleanup also fails.
- CLI tests cover dry-run parsing, dry-run output, complete credential
  requirements for live writes, and explicit live database construction.
- `make check` runs with Python bytecode disabled and fails if `.pyc` or `.pyo`
  files are present in the checkout.
- `make root-test` proves every public target accepts only the supported
  `python2` or `python3` selectors, keeps shell and bytecode policy under
  repository control, and rejects preload and Makefile-list overrides.
- `make check` also requires completed canonical plans under `docs/plans`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Live PostgreSQL runs require operator-provided database connection fields.
  Keep credentials in the shell or a local secret manager; do not commit them.

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
- See `docs/plans/2026-06-09-product-link-scheme-guard.md` for product-link
  scheme validation and relative-link normalization.
- See `docs/plans/2026-06-14-product-link-userinfo-guard.md` for rejecting
  credential-bearing product links parsed from remote markup.
- See `docs/plans/2026-06-09-structured-db-connect.md` for structured
  database connection parameters.
- See `docs/plans/2026-06-09-database-close-order.md` for cursor-first
  database cleanup coverage.
- See `docs/plans/2026-06-09-database-close-finally.md` for connection cleanup
  when cursor close fails.
- See `docs/plans/2026-06-09-cli-dry-run.md` for the command-line dry-run and
  live database credential guard.
- See `docs/plans/2026-06-09-source-url-scheme-guard.md` for source page URL
  scheme validation.
- See `docs/plans/2026-06-09-bytecode-free-verification.md` for bytecode-free
  verification coverage.
- See `docs/plans/2026-06-10-ci-baseline.md` for the GitHub Actions `make
  check` baseline.
- See `docs/plans/2026-06-10-hosted-legacy-validation.md` for the enforced
  Python 2.7 offline test boundary.
- See `docs/plans/2026-06-10-http-response-cleanup.md` for scraper response
  cleanup on successful and failed reads.
- See `docs/plans/2026-06-12-response-body-size-limit.md` for the bounded
  response memory contract.
- See `docs/plans/2026-06-12-same-host-redirect-boundary.md` for pre-request
  redirect target validation and its explicit DNS-rebinding limitation.
- See `docs/plans/2026-06-14-make-root-override-protection.md` for the
  caller-resistant, location-independent offline verification root.
- See `docs/plans/2026-06-21-make-authority-isolation.md` for constrained
  dual-runtime Make authority and hostile-input regression coverage.
- See `docs/plans/2026-06-15-python3-compatibility.md` for the Python 2.7 and
  Python 3.12 offline compatibility boundary.
- See `docs/plans/2026-06-16-content-type-boundary.md` for the declared HTML
  response media-type boundary.
- See `docs/plans/2026-06-16-product-construction-database-cleanup.md` for
  cleanup when source or network-limit validation fails after database setup.
- See `docs/plans/2026-06-17-database-cursor-construction-cleanup.md` for
  connection cleanup when cursor construction prevents database setup from
  completing.
- See `docs/plans/2026-06-17-product-construction-primary-error.md` for cleanup
  that preserves the Product construction primary error over close failures.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
