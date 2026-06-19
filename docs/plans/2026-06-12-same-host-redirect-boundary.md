# Same-Host Redirect Boundary

## Status: Completed

## Context

The scraper validates the operator-provided source URL, applies a timeout, caps
the response body, and closes every response. Python 2 `urllib2` still follows
redirects by default, so an approved public source can redirect the request to
a different hostname, embedded credentials, or a non-web target before the
body controls run.

## Priority

Redirect validation must happen before the follow-up request. Python 2 exposes
`HTTPRedirectHandler.redirect_request` for that decision, and `build_opener`
replaces its default redirect handler when supplied a subclass instance. A
same-source-host policy narrows the server-side request surface without adding
dependencies or making live network calls in verification.

## Requirements

- R1. Install a custom Python 2 `HTTPRedirectHandler` on every product read.
- R2. Resolve relative redirect locations against the current request URL.
- R3. Permit only HTTP(S) redirects whose hostname matches the original source
  hostname case-insensitively and whose effective port remains on the approved
  origin.
- R4. Permit same-host HTTP-to-HTTPS upgrades and same-host relative paths.
- R5. Reject cross-host, alternate-port, scheme-relative cross-host,
  HTTPS-to-HTTP downgrade, non-web, hostless, and username/password-bearing
  redirect targets before they are opened.
- R6. Raise a bounded `urllib2.HTTPError` that names only the policy failure and
  does not echo credentials or the rejected target.
- R7. Preserve timeout, body-size, response-close, parser, and database behavior.
- R8. Add offline tests and fail-closed source/docs contracts for the handler,
  opener installation, allowed redirects, and rejected targets.

## Scope Boundaries

- Do not perform DNS resolution or claim protection from DNS rebinding.
- Do not block the operator from explicitly choosing a private source URL; this
  change limits server-controlled redirects away from that chosen hostname.
- Do not make live requests or install the archived scraper dependencies.
- Do not modernize the Python 2 runtime in this change.

## Verification Plan

- focused Python 2 redirect-handler tests
- `python2 -B -m unittest discover -s tests`
- `make check` locally, outside the checkout, and in the exact digest-pinned
  network-isolated Python 2.7.18 container
- focused valid-Git-metadata redirect mutations
- workflow YAML, Python syntax, bytecode, secret, generated-artifact, and
  `git diff --check` audits

## Work Completed

- Added a Python 2 `HTTPRedirectHandler` that stores the normalized source
  hostname and is installed on every `Product.read()` opener.
- Rejected malformed scheme-without-authority locations before `urljoin`, then
  validated the resolved redirect scheme, host, and absence of user info before
  delegating allowed redirects to the standard handler.
- Converted malformed URL parse failures to the same constant policy error and
  normalized malformed source parsing to the existing generic source error.
- Allowed relative paths and case-insensitive same-host HTTP-to-HTTPS upgrades
  on standard ports while rejecting HTTPS-to-HTTP downgrades and alternate
  service ports.
- Raised a constant-policy `HTTPError` using a credential-free source origin so
  rejected targets and embedded credentials are not echoed.
- Expanded the offline Python 2 suite from 25 to 28 tests and aligned the
  source/docs checker, README, security guidance, vision, and changelog.

## Verification

- `python2 -B -m unittest discover -s tests -p 'test_scrape.py'` passed 28 tests.
- `make check` and root-independent `make -f /path/to/Makefile check` passed the
  documentation contract, 17 workflow mutations, Python 2 syntax, and all 28
  offline tests.
- The exact digest-pinned Python 2.7.18 container passed `make check` with a
  read-only source snapshot and disabled networking.
- Fifteen valid-Git-metadata mutations were rejected: opener wiring, rejection
  helper, host, user, password, malformed authority, downgrade, parsed source
  hostname, scheme, alternate-port enforcement, rejected-target disclosure,
  allowed-relative test, README test count, security documentation, and
  incomplete-plan regressions.
- Workflow YAML parsed, every Python source compiled under Python 2, no bytecode
  artifacts were present, and high-confidence secret and `git diff --check`
  audits passed.
