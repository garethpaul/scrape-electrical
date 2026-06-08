# Issue 2: Parameterize Product Inserts

## Context

GitHub issue: `garethpaul/scrape-electrical#2`

`Database.insert` builds an `INSERT` statement by concatenating scraped product values into SQL. Product names, links, and prices come from parsed HTML and can break queries or alter the statement.

## Plan

1. Use psycopg2 value placeholders for scraped product fields.
2. Validate and quote the table identifier separately, since SQL identifiers cannot be bound as values.
3. Preserve the existing database API and commit behavior.
4. Add a source-level verifier for the SQL safety contract.

## Verification

- Run `bash scripts/check-baseline.sh`.
- Run `git diff --check`.
