#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
import re
import sys

from workflow_contract import validate as validate_workflow


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS_PLANS = os.path.join(ROOT, 'docs', 'plans')
CANONICAL_PLAN = os.path.join(DOCS_PLANS, '2026-06-08-scrape-electrical-baseline.md')
LINK_SCHEME_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-product-link-scheme-guard.md')
CLI_DRY_RUN_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-cli-dry-run.md')
BYTECODE_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-bytecode-free-verification.md')
CI_PLAN = os.path.join(DOCS_PLANS, '2026-06-10-ci-baseline.md')
HOSTED_LEGACY_PLAN = os.path.join(DOCS_PLANS, '2026-06-10-hosted-legacy-validation.md')
RESPONSE_BODY_LIMIT_PLAN = os.path.join(DOCS_PLANS, '2026-06-12-response-body-size-limit.md')
REDIRECT_BOUNDARY_PLAN = os.path.join(DOCS_PLANS, '2026-06-12-same-host-redirect-boundary.md')
REDIRECT_HOP_LIMIT_PLAN = os.path.join(DOCS_PLANS, '2026-06-13-redirect-hop-limit.md')
SOURCE_USERINFO_PLAN = os.path.join(DOCS_PLANS, '2026-06-13-source-url-userinfo-guard.md')
MAKE_ROOT_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-make-root-override-protection.md')
PRODUCT_LINK_USERINFO_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-product-link-userinfo-guard.md')
MALFORMED_PRODUCT_LINK_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-malformed-product-link-boundary.md')
CI_WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'check.yml')
MAKEFILE = os.path.join(ROOT, 'Makefile')


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, 'r') as handle:
        return handle.read()


failures = []

for required_path in (
        CANONICAL_PLAN,
        LINK_SCHEME_PLAN,
        CLI_DRY_RUN_PLAN,
        BYTECODE_PLAN,
        CI_PLAN,
        HOSTED_LEGACY_PLAN,
        RESPONSE_BODY_LIMIT_PLAN,
        REDIRECT_BOUNDARY_PLAN,
        REDIRECT_HOP_LIMIT_PLAN,
        SOURCE_USERINFO_PLAN,
        MAKE_ROOT_PLAN,
        PRODUCT_LINK_USERINFO_PLAN,
        MALFORMED_PRODUCT_LINK_PLAN,
        CI_WORKFLOW):
    if not os.path.isfile(required_path):
        failures.append('%s is missing' % rel(required_path))

plans = sorted(glob.glob(os.path.join(DOCS_PLANS, '*.md')))
if not plans:
    failures.append('docs/plans must contain at least one completed plan')

for plan_path in plans:
    plan = read(plan_path)
    if 'Status: Completed' not in plan or 'make check' not in plan:
        failures.append('%s must record completed status and make check verification' % rel(plan_path))

bytecode_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if '.git' in dirnames:
        dirnames.remove('.git')
    if '__pycache__' in dirnames:
        bytecode_files.append(rel(os.path.join(dirpath, '__pycache__')))
        dirnames.remove('__pycache__')
    for filename in filenames:
        if filename.endswith(('.pyc', '.pyo')):
            bytecode_files.append(rel(os.path.join(dirpath, filename)))

if bytecode_files:
    failures.append('Python bytecode must not be present: %s' % ', '.join(sorted(bytecode_files)))

workflow = read(CI_WORKFLOW) if os.path.isfile(CI_WORKFLOW) else ''
for requirement in validate_workflow(workflow):
    failures.append('GitHub Actions workflow must %s' % requirement)

makefile = read(MAKEFILE) if os.path.isfile(MAKEFILE) else ''
root_declaration = 'override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))'
root_assignments = [
    line for line in makefile.splitlines()
    if re.match(r'^(?:override\s+)?ROOT\s*[:?+]?=', line)
]
if not makefile.startswith(root_declaration + '\n') or root_assignments != [root_declaration]:
    failures.append('Makefile must define exactly one protected repository-derived ROOT declaration first')
required_makefile_phrases = (
    root_declaration,
    'PYTHON ?= python2',
    '$(PYTHON) -B "$(ROOT)/scripts/check-docs-plans.py"',
    '$(PYTHON) -B "$(ROOT)/scripts/test_workflow_contract.py"',
    '$(PYTHON) -B -m unittest discover -s tests',
    'verify: lint contract-test test',
)
for phrase in required_makefile_phrases:
    if phrase not in makefile:
        failures.append('Makefile must contain %s' % phrase)
if 'command -v $(PYTHON)' in makefile or 'unavailable; skipping legacy Python 2 tests' in makefile:
    failures.append('Makefile must require Python 2 scraper verification instead of skipping it')

if os.path.isfile(MAKE_ROOT_PLAN):
    make_root_plan = read(MAKE_ROOT_PLAN)
    for evidence in (
            'Status: Completed',
            '`make ROOT=/tmp check` passed',
            'all six public Make aliases passed',
            'Six hostile mutations were rejected',
            'digest-pinned Python 2.7.18'):
        if evidence not in make_root_plan:
            failures.append('%s must record verification evidence %s' % (rel(MAKE_ROOT_PLAN), evidence))

readme = read(os.path.join(ROOT, 'README.md'))
if rel(MAKE_ROOT_PLAN) not in readme:
    failures.append('README.md must reference %s' % rel(MAKE_ROOT_PLAN))
vision = read(os.path.join(ROOT, 'VISION.md'))
changes = read(os.path.join(ROOT, 'CHANGES.md'))
scrape_source = read(os.path.join(ROOT, 'scrape.py'))
if 'psycopg2.connect("user=%s password=%s host=%s dbname=%s"' in scrape_source:
    failures.append('scrape.py must not build a psycopg2 connection string by interpolation')
if 'psycopg2.connect(\n            user=self.dbuser,' not in scrape_source:
    failures.append('scrape.py must pass database connection fields as psycopg2 keyword arguments')
if 'from urlparse import urljoin, urlparse' not in scrape_source:
    failures.append('scrape.py must import Python 2 URL normalization helpers')
if 'def normalized_link(self, href):' not in scrape_source:
    failures.append('scrape.py must normalize parsed product links before database insertion')
if 'self.url = self.normalized_source_url(url)' not in scrape_source:
    failures.append('scrape.py must validate the source URL before network reads')
if 'def normalized_source_url(self, url):' not in scrape_source:
    failures.append('scrape.py must normalize and validate source URLs')
if "raise ValueError('source URL must use http or https and include a host')" not in scrape_source:
    failures.append('scrape.py must reject non-HTTP(S) source URLs before urllib2 opens them')
if "parsed_url.scheme not in ('http', 'https')" not in scrape_source:
    failures.append('scrape.py must reject parsed product links that are not HTTP(S)')
if 'urljoin(self.url, href.strip())' not in scrape_source:
    failures.append('scrape.py must resolve relative product links against the source URL')
for phrase in (
        'link_host = parsed_url.hostname',
        'parsed_url.port',
        'except ValueError:\n            return None',
        'not parsed_url.netloc or link_host is None'):
    if phrase not in scrape_source:
        failures.append('scrape.py must reject malformed product link authorities via %r' % phrase)
if scrape_source.count('parsed_url.username is not None or parsed_url.password is not None') < 2:
    failures.append('scrape.py must reject credentials in source and product links')
if 'import argparse' not in scrape_source:
    failures.append('scrape.py must expose a Python 2 argparse CLI')
if 'class DryRunDatabase(object):' not in scrape_source:
    failures.append('scrape.py must provide a dry-run database sink')
if "'--dry-run'" not in scrape_source:
    failures.append('scrape.py CLI must expose --dry-run')
if 'def database_from_options(options):' not in scrape_source:
    failures.append('scrape.py must centralize CLI database creation')
if 'if options.dry_run:' not in scrape_source:
    failures.append('scrape.py must bypass PostgreSQL creation during dry-run')
if "'missing database options for live writes:" not in scrape_source:
    failures.append('scrape.py must reject live CLI writes without complete DB options')
if "if __name__ == '__main__':\n    run_cli()" not in scrape_source:
    failures.append('scrape.py must run the CLI entry point when executed directly')
for phrase in (
        'DEFAULT_MAX_RESPONSE_BYTES = 5 * 1024 * 1024',
        'max_response_bytes=DEFAULT_MAX_RESPONSE_BYTES',
        'isinstance(max_response_bytes, bool) or',
        'not isinstance(max_response_bytes, (int, long)) or',
        'response.read(self.max_response_bytes + 1)',
        'if len(body) > self.max_response_bytes:',
        "'--max-response-bytes'",
        'max_response_bytes=options.max_response_bytes'):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain response body size limit fragment %r' % phrase)
for phrase in (
        'class SameHostRedirectHandler(urllib2.HTTPRedirectHandler):',
        'max_repeats = 2',
        'max_redirections = 5',
        'self.source_port = parsed_source.port or self.default_port(self.source_scheme)',
        'def default_port(self, scheme):',
        'def rejected_redirect(self, code, headers, fp):',
        'raise self.rejected_redirect(code, headers, fp)',
        'raw_redirect = urlparse(newurl)',
        'current_scheme = urlparse(req.get_full_url()).scheme',
        'not (raw_redirect.scheme and not raw_redirect.netloc)',
        'redirect_url = urljoin(req.get_full_url(), newurl)',
        "parsed_redirect.scheme in ('http', 'https')",
        "not (current_scheme == 'https' and parsed_redirect.scheme == 'http')",
        'redirect_port == self.source_port',
        'standard_https_upgrade = (',
        '(same_origin or standard_https_upgrade)',
        'redirect_host.lower() == self.source_host',
        'parsed_redirect.username is None',
        'parsed_redirect.password is None',
        "'redirect target violates same-host policy'",
        'urllib2.build_opener(SameHostRedirectHandler(self.url))'):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain same-host redirect fragment %r' % phrase)
if 'source_host = parsed_url.hostname' not in scrape_source or 'source_host is None' not in scrape_source:
    failures.append('scrape.py must require a parsed source hostname before network reads')
if ('parsed_url.username is not None or parsed_url.password is not None' not in scrape_source or
        "raise ValueError('source URL must not include credentials')" not in scrape_source):
    failures.append('scrape.py must reject source URL credentials before network reads')

test_source = read(os.path.join(ROOT, 'tests', 'test_scrape.py'))
for test_name in (
        'test_read_accepts_body_at_configured_limit',
        'test_read_rejects_and_closes_oversized_body',
        'test_product_rejects_non_positive_response_limit',
        'test_product_rejects_non_integer_response_limit',
        'test_run_cli_forwards_response_limit'):
    if test_name not in test_source:
        failures.append('tests/test_scrape.py must retain %s' % test_name)
for test_name in (
        'test_redirect_handler_has_explicit_hop_limits',
        'test_redirect_handler_allows_same_host_relative_redirect',
        'test_redirect_handler_allows_same_host_https_upgrade',
        'test_redirect_handler_rejects_unsafe_targets_without_echoing_them'):
    if test_name not in test_source:
        failures.append('tests/test_scrape.py must retain %s' % test_name)
if 'test_product_rejects_source_url_credentials_without_echoing_them' not in test_source:
    failures.append('tests/test_scrape.py must retain source URL credential rejection coverage')
if 'test_find_products_skips_credential_bearing_links' not in test_source:
    failures.append('tests/test_scrape.py must retain product link credential rejection coverage')
if 'test_find_products_skips_malformed_links_and_continues' not in test_source:
    failures.append('tests/test_scrape.py must retain malformed product link continuation coverage')

link_scheme_plan = read(LINK_SCHEME_PLAN) if os.path.isfile(LINK_SCHEME_PLAN) else ''
if 'Status: Completed' not in link_scheme_plan or 'Product.normalized_link()' not in link_scheme_plan:
    failures.append('%s must record completed product link scheme work' % rel(LINK_SCHEME_PLAN))

cli_plan = read(CLI_DRY_RUN_PLAN) if os.path.isfile(CLI_DRY_RUN_PLAN) else ''
if 'Status: Completed' not in cli_plan or '--dry-run' not in cli_plan:
    failures.append('%s must record completed CLI dry-run work' % rel(CLI_DRY_RUN_PLAN))

security = read(os.path.join(ROOT, 'SECURITY.md'))
if 'non-web link schemes' not in security or 'relative product links' not in security:
    failures.append('SECURITY.md must document product link scheme and relative URL boundaries')
if 'Source page URLs must also use HTTP(S)' not in security:
    failures.append('SECURITY.md must document source URL scheme validation')
if 'GitHub Actions' not in readme or 'GitHub Actions' not in vision or 'GitHub Actions' not in security or 'GitHub Actions' not in changes:
    failures.append('docs must mention the GitHub Actions CI baseline')
if ('response body size limit' not in readme or
        'response body size limit' not in vision or
        'response body size limit' not in security or
        'response body size limit' not in changes):
    failures.append('docs must describe the response body size limit')
if ('same-host redirect' not in readme or
        'same-host redirect' not in vision or
        'same-host redirect' not in security or
        'same-host redirect' not in changes):
    failures.append('docs must describe the same-host redirect boundary')
if ('redirect hop limit' not in readme or
        'redirect hop limit' not in vision or
        'redirect hop limit' not in security or
        'redirect hop limit' not in changes):
    failures.append('docs must describe the redirect hop limit')
if ('source URL credentials' not in readme or
        'source URL credentials' not in vision or
        'source URL credentials' not in security or
        'source URL credentials' not in changes):
    failures.append('docs must describe the source URL credential boundary')
if ('product link credentials' not in readme or
        'product link credentials' not in vision or
        'product link credentials' not in security or
        'product link credentials' not in changes):
    failures.append('docs must describe the product link credential boundary')
if any(re.search(r'malformed\s+product\s+links', document) is None
       for document in (readme, vision, security, changes)):
    failures.append('docs must describe the malformed product link boundary')
if 'all 32' not in readme:
    failures.append('README.md must record the complete 32-test offline suite')

product_link_userinfo_plan = read(PRODUCT_LINK_USERINFO_PLAN) if os.path.isfile(PRODUCT_LINK_USERINFO_PLAN) else ''
for evidence in (
        'Status: Completed',
        'repository and external-directory `make check` passed',
        'hostile product-link userinfo mutations were rejected',
        'generated-artifact and credential-pattern audits passed'):
    if evidence not in product_link_userinfo_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(PRODUCT_LINK_USERINFO_PLAN), evidence))

malformed_product_link_plan = read(MALFORMED_PRODUCT_LINK_PLAN) if os.path.isfile(MALFORMED_PRODUCT_LINK_PLAN) else ''
for evidence in (
        'Status: Completed',
        'repository and external-directory `make check` passed',
        'hostile malformed-link mutations were rejected',
        'generated-artifact and credential-pattern audits passed'):
    if evidence not in malformed_product_link_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(MALFORMED_PRODUCT_LINK_PLAN), evidence))

ci_plan = read(CI_PLAN) if os.path.isfile(CI_PLAN) else ''
if 'Status: Completed' not in ci_plan or 'make check' not in ci_plan:
    failures.append('%s must record completed CI baseline verification' % rel(CI_PLAN))

if failures:
    print('Documentation plan checks failed:\n- %s' % '\n- '.join(failures), file=sys.stderr)
    sys.exit(1)

print('Documentation plan checks passed')
