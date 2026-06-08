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
- Treat Python 2, raw SQL, and incomplete CLI wiring as legacy risks

Next priorities:

- Add argument parsing and a dry-run mode
- Replace string-built SQL with parameterized queries
- Document target-site permission, rate limits, and data retention
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
- Credential files
- Anti-blocking or evasion behavior
- Large scraped datasets

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
