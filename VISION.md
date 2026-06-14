## Scrape Electrical Vision

Scrape Electrical is a legacy Python script intended to scrape product data
from a web page and insert product name, link, and price fields into PostgreSQL.

The repository is useful as a cautionary scraping/database prototype: it shows
the intended CLI arguments, database connection shape, HTML parsing approach,
and several safety gaps that must be addressed before use.

The goal is to preserve the prototype while making responsible scraping and SQL
safety the first improvement priorities.

The current focus is:

Priority:

- Preserve the scrape-to-PostgreSQL intent
- Keep database credentials passed by the operator, not committed
- Avoid encouraging bypass headers or aggressive scraping
- Bound live network reads so stalled targets do not hang indefinitely
- Keep a configurable response body size limit ahead of HTML parsing
- Close source-page responses on successful and failed body reads
- Require source page URLs to use HTTP(S) before network reads
- Reject source URL credentials before request construction
- Keep a same-host redirect boundary ahead of follow-up network requests
- Keep an explicit redirect hop limit on same-host chains and loops
- Skip incomplete product cards instead of aborting the scrape
- Resolve product links against the source URL and reject non-web schemes
- Reject product link credentials parsed from remote markup before persistence
- Reject malformed product links without aborting later safe product rows
- Pass database connection fields as structured driver parameters
- Require a dry-run or complete database credentials for command-line runs
- Keep database cursor cleanup ordered before connection teardown
- Keep connection cleanup attempted when cursor cleanup fails
- Keep completed maintenance plans under `docs/plans`
- Keep verification runs from leaving Python bytecode in the checkout
- Keep GitHub Actions running the complete offline Python 2 scraper suite with
  credential-free checkout and no live dependency installation
- Keep hosted workflow policy protected by dependency-free hostile mutations
- Treat Python 2, raw SQL, and incomplete CLI wiring as legacy risks

Next priorities:

- Document target-site permission, rate limits, and data retention
- Add rate limiting or backoff before broad live scraping
- Expand mocked HTML and database tests before parser changes

Contribution rules:

- One PR = one focused parser, database, CLI, safety, or documentation change.
- Do not commit database credentials or scraped data.
- Keep scraping respectful of target site terms and load.
- Add tests before broad parser changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Scrapers can overload sites and raw SQL can corrupt or expose data. This script
should not be run against third-party sites without permission, and database
writes should be parameterized before production use.

## What We Will Not Merge (For Now)

- SQL string concatenation for user-provided values
- Interpolated PostgreSQL connection strings for operator-provided credentials
- Credential files
- Command-line live writes without explicit database credentials
- Anti-blocking or evasion behavior
- Large scraped datasets

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
