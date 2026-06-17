# Security Policy

## Supported Versions

The supported security scope for `scrape-electrical` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Personal scrape for * electrical with a given URL

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/scrape-electrical` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

Product parsing rejects non-web link schemes. It normalizes relative product links
against the source page before database writes. Preserve that boundary when
changing scraper targets or product-link parsing.
Remote product link credentials are rejected before database writes or dry-run
output.
Remote malformed product links are rejected at the row boundary without being
logged and without stopping later safe product rows.
Source page URLs must also use HTTP(S) and include a host before the scraper
opens them with `urllib2`.
Scraper timeouts must be finite positive numbers before network setup.
Malformed source URL authorities, including invalid explicit ports, are
rejected before opener construction without echoing the supplied URL.
The scraper rejects source URL credentials before request construction so
userinfo cannot be carried into an initial fetch.
The same-host redirect boundary allows relative and same-host HTTPS redirects
but rejects cross-host, alternate-port, HTTPS-to-HTTP downgrade, non-web,
hostless, and credential-bearing targets before the follow-up request. It does
not claim DNS-rebinding protection.
The explicit redirect hop limit permits five total redirects and two repeats of
the same target, bounding same-host loops and long chains.
HTTP responses must close after body reads, including parser or transport
failure paths, so repeated scraping does not leak network resources.
The default 5 MiB response body size limit rejects oversized pages before HTML
parsing while still closing the response; increases require explicit CLI input.
Bounded response reads continue through legal short response chunks until EOF or
one byte beyond the limit, preventing fragmented bodies from being silently
truncated or escaping complete size enforcement.
Source requests require identity content encoding, and responses that declare
any other content encoding are rejected before body reads.
Source requests advertise HTML, and explicit non-HTML content types are
rejected before body reads without echoing the supplied header value. Missing
`Content-Type` remains accepted for historical endpoint compatibility.
Product construction primary error preservation keeps validation and
interruption failures authoritative when database cleanup also fails, avoiding
misleading startup diagnostics while still attempting resource cleanup.
GitHub Actions runs the complete offline gate under Python 2.7 and Python 3.12,
using a digest-pinned legacy container and an immutable setup action. Neither
lane installs live scraping or database dependencies or receives database
credentials.
CI checkout credentials stay disabled, actions remain pinned by commit, and
permissions remain read-only. Hostile mutations reject contradictory
credentials, dependency installation, and other workflow-policy drift.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
