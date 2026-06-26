# Responsible Scraping Guide

This repository is an educational single-page scraper, not a general-purpose
crawler. Its technical ability to fetch a URL does not establish permission to
use that URL or retain its data.

## Before Any Live Request

Obtain explicit written permission from the target-site owner or an authorized
representative. Record the approved host, paths, purpose, time window, request
budget, contact, allowed fields, storage location, and retention deadline. Keep
that approval outside the repository if it contains private contact or contract
information.

Review the site's terms and applicable policy with the owner. Fetch and honor
`robots.txt` for automated access, but remember that robots.txt is not
authorization. RFC 9309 defines crawler access rules and explicitly separates
them from access authorization: <https://www.rfc-editor.org/rfc/rfc9309.html>.

Use `--dry-run` against an owner-provided fixture or staging page first. Do not
start when scope is ambiguous, credentials are embedded in a URL, the approved
window has expired, or the requested fields exceed the recorded purpose.

## Request Pace And Stop Conditions

This script has no automatic rate limiter or retry policy. Keep one request at
a time and stay within the site owner's written request budget. Do not use it
for broad or repeated scraping until a separate change adds tested pacing and
backoff.

Stop the run on any unexpected redirect, authorization challenge, block page,
CAPTCHA, timeout pattern, connection instability, or response outside the
approved paths. On a `429` or `503`, do not immediately retry. Honor a valid
`Retry-After` value and require operator review before another request. RFC 9110
defines `Retry-After` as either an HTTP date or delay in seconds:
<https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after>.

Stop immediately if the owner asks, the request budget is exhausted, response
latency or errors increase, or the content suggests the run is causing load.
This sample must not be adapted to evade blocks, rotate identities, bypass
access controls, or imitate unrelated clients.

## Data Minimization And Retention

Collect only the approved product name, public product URL, and price fields.
Do not collect personal data, account-only content, secrets, session tokens, or
unrelated page content. The script does not need raw HTML after parsing.

Set a retention deadline before collection. Store only the minimum normalized
rows needed for the approved purpose, restrict database access, and document
who can delete them. If debugging requires temporary captures, delete raw
responses as soon as the approved investigation ends and never commit them.
Delete derived rows when permission is withdrawn, the purpose ends, or the
retention deadline arrives.

## Run Record

For each approved run, retain a privacy-safe record containing:

- approval reference and owner contact channel;
- exact source host and approved paths;
- start/end time, request count, and final status;
- configured timeout and response-size limit;
- any `Retry-After`, block, error, or stop event;
- stored fields, storage owner, and deletion date.

Do not put credentials, private agreements, raw responses, scraped datasets, or
personal data in GitHub issues, pull requests, logs, fixtures, or commits.
