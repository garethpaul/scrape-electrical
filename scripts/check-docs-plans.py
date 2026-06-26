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
REDIRECT_REJECTION_CLEANUP_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-19-rejected-redirect-response-cleanup.md'
)
SOURCE_USERINFO_PLAN = os.path.join(DOCS_PLANS, '2026-06-13-source-url-userinfo-guard.md')
MAKE_ROOT_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-make-root-override-protection.md')
MAKE_AUTHORITY_PLAN = os.path.join(DOCS_PLANS, '2026-06-21-make-authority-isolation.md')
PRODUCT_LINK_USERINFO_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-product-link-userinfo-guard.md')
MALFORMED_PRODUCT_LINK_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-malformed-product-link-boundary.md')
MALFORMED_SOURCE_URL_PLAN = os.path.join(DOCS_PLANS, '2026-06-15-malformed-source-url-boundary.md')
TIMEOUT_VALIDATION_PLAN = os.path.join(DOCS_PLANS, '2026-06-15-finite-positive-timeout-validation.md')
PYTHON3_COMPATIBILITY_PLAN = os.path.join(DOCS_PLANS, '2026-06-15-python3-compatibility.md')
COMPLETE_BOUNDED_READ_PLAN = os.path.join(DOCS_PLANS, '2026-06-16-complete-bounded-response-read.md')
CONTENT_ENCODING_PLAN = os.path.join(DOCS_PLANS, '2026-06-16-content-encoding-boundary.md')
CONTENT_TYPE_PLAN = os.path.join(DOCS_PLANS, '2026-06-16-content-type-boundary.md')
CONSTRUCTION_CLEANUP_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-16-product-construction-database-cleanup.md'
)
DATABASE_CONSTRUCTOR_CLEANUP_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-17-database-cursor-construction-cleanup.md'
)
PRODUCT_CONSTRUCTION_PRIMARY_ERROR_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-17-product-construction-primary-error.md'
)
RESPONSIBLE_USE_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-25-responsible-scraping-guide.md'
)
RESPONSIBLE_USE_GUIDE = os.path.join(ROOT, 'RESPONSIBLE_USE.md')
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
        REDIRECT_REJECTION_CLEANUP_PLAN,
        SOURCE_USERINFO_PLAN,
        MAKE_ROOT_PLAN,
        MAKE_AUTHORITY_PLAN,
        PRODUCT_LINK_USERINFO_PLAN,
        MALFORMED_PRODUCT_LINK_PLAN,
        MALFORMED_SOURCE_URL_PLAN,
        TIMEOUT_VALIDATION_PLAN,
        PYTHON3_COMPATIBILITY_PLAN,
        COMPLETE_BOUNDED_READ_PLAN,
        CONTENT_ENCODING_PLAN,
        CONTENT_TYPE_PLAN,
        CONSTRUCTION_CLEANUP_PLAN,
        DATABASE_CONSTRUCTOR_CLEANUP_PLAN,
        PRODUCT_CONSTRUCTION_PRIMARY_ERROR_PLAN,
        RESPONSIBLE_USE_PLAN,
        RESPONSIBLE_USE_GUIDE,
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
root_declaration = "override ROOT := $(shell sed_path=/usr/bin/sed; [ -x \"$$sed_path\" ] || sed_path=/bin/sed; [ -x \"$$sed_path\" ] || exit 1; path=$$(printf '%s' '$(subst ','\"'\"',$(MAKEFILE_LIST))' | \"$$sed_path\" 's/^ //'); [ -f \"$$path\" ] || exit 1; directory=$${path%/*}; [ \"$$directory\" != \"$$path\" ] || directory=.; CDPATH= cd \"$$directory\" && pwd -P)"
root_assignments = [
    line for line in makefile.splitlines()
    if re.match(r'^(?:override\s+)?ROOT\s*[:?+]?=', line)
]
required_makefile_phrases = (
    'override SHELL := /bin/sh',
    'override .SHELLFLAGS := -c',
    '.SECONDEXPANSION:',
    '$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)',
    'override MAKEFILES :=',
    '$(error MAKEFILE_LIST must not be overridden)',
    root_declaration,
    'export ROOT',
    '$(error repository Makefile path could not be resolved)',
    '$(error repository Makefile must be loaded alone)',
    'PYTHON ?= python2',
    '$(error PYTHON must be exactly python2 or python3)',
    'override PYTHON := $(value PYTHON)',
    'override PYTHONDONTWRITEBYTECODE := 1',
    'export PYTHONDONTWRITEBYTECODE',
    'root-test:',
    '\t/bin/sh "$$ROOT/scripts/test-makefile-root.sh"',
    'verify: root-test lint contract-test test',
)
if root_assignments != [root_declaration]:
    failures.append('Makefile must define exactly one safe repository-derived ROOT declaration')
for phrase in required_makefile_phrases:
    if phrase not in makefile:
        failures.append('Makefile must preserve verification authority phrase %s' % phrase)
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

root_test = os.path.join(ROOT, 'scripts', 'test-makefile-root.sh')
if os.path.isfile(root_test):
    root_test_text = read(root_test)
    for evidence in (
            '77 executed target/authority cases',
            '21 invalid-runtime, function, file-list, preload, or multi-Makefile rejections',
            'PYTHON must be exactly python2 or python3',
            'MAKEFILE_LIST must not be overridden',
            'MAKEFILES must be empty'):
        if evidence not in root_test_text:
            failures.append('%s must preserve %r' % (rel(root_test), evidence))
else:
    failures.append('%s is missing' % rel(root_test))

if os.path.isfile(MAKE_AUTHORITY_PLAN):
    make_authority_plan = read(MAKE_AUTHORITY_PLAN)
    for evidence in (
            'Status: Completed',
            '`make root-test` passed 77 target/authority cases and 21 rejection cases',
            '`make check PYTHON=python2` and `make check PYTHON=python3` passed'):
        if evidence not in make_authority_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(MAKE_AUTHORITY_PLAN), evidence))

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
for phrase in (
        'try:\n            self.cur = self.conn.cursor()',
        'except BaseException:\n            self._close_connection_after_cursor_failure()\n            raise',
        'def _close_connection_after_cursor_failure(self):',
        'try:\n            self.conn.close()\n        except BaseException:\n            pass'):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain database constructor cleanup %r' % phrase)
for phrase in (
        'try:\n    import urllib2',
        'from urlparse import urljoin, urlparse',
        'except ImportError:',
        'import urllib.error',
        'import urllib.request as urllib2',
        'from urllib.parse import urljoin, urlparse',
        'urllib2.HTTPError = urllib.error.HTTPError',
        'try:\n    INTEGER_TYPES = (int, long)',
        'except NameError:\n    INTEGER_TYPES = (int,)',
        'try:\n    STRING_TYPES = (basestring,)',
        'except NameError:\n    STRING_TYPES = (str,)'):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain dual-runtime compatibility fragment %r' % phrase)
if 'def normalized_link(self, href):' not in scrape_source:
    failures.append('scrape.py must normalize parsed product links before database insertion')
if 'self.url = self.normalized_source_url(url)' not in scrape_source:
    failures.append('scrape.py must validate the source URL before network reads')
if 'def normalized_source_url(self, url):' not in scrape_source:
    failures.append('scrape.py must normalize and validate source URLs')
if 'not isinstance(url, STRING_TYPES) or not url.strip()' not in scrape_source:
    failures.append('scrape.py must reject non-string source URL values before normalization')
if 'not isinstance(href, STRING_TYPES) or not href.strip()' not in scrape_source:
    failures.append('scrape.py must skip non-string product links before normalization')
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
constructor_cleanup = (
    '    try:\n'
    '        p = Product(\n'
    '            database,\n'
    '            url,\n'
    '            timeout=timeout,\n'
    '            max_response_bytes=max_response_bytes\n'
    '        )\n'
    '    except BaseException:\n'
    '        _close_database_after_product_construction_failure(database)\n'
    '        raise\n'
    '    # find products and place them in a database\n'
    '    p.find()'
)
if constructor_cleanup not in scrape_source:
    failures.append('scrape.py must preserve primary Product construction errors during cleanup')
for phrase in (
        'def _close_database_after_product_construction_failure(database):',
        'try:\n        database.close()\n    except BaseException:\n        pass'):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain non-masking Product construction cleanup %r' % phrase)
for phrase in (
        'DEFAULT_MAX_RESPONSE_BYTES = 5 * 1024 * 1024',
        'max_response_bytes=DEFAULT_MAX_RESPONSE_BYTES',
        'isinstance(max_response_bytes, bool) or',
        'not isinstance(max_response_bytes, INTEGER_TYPES) or',
        'remaining = self.max_response_bytes + 1',
        'while remaining > 0:',
        'chunk = response.read(remaining)',
        'if not chunk:',
        'remaining -= len(chunk)',
        'body = chunks[0][:0].join(chunks)',
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
        'error = urllib2.HTTPError(',
        'error.close()',
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
if 'source_host = parsed_url.hostname' not in scrape_source or 'not source_host' not in scrape_source:
    failures.append('scrape.py must require a parsed source hostname before network reads')
for phrase in (
        'source_port = parsed_url.port',
        "source_authority = parsed_url.netloc.rsplit('@', 1)[-1]",
        "explicit_port = re.search(r'(?:\\]|[^:]):([^:]*)$', source_authority)",
        'if explicit_port is not None and source_port is None:'):
    if phrase not in scrape_source:
        failures.append('scrape.py must reject malformed source URL authorities via %r' % phrase)
if ('parsed_url.username is not None or parsed_url.password is not None' not in scrape_source or
        "raise ValueError('source URL must not include credentials')" not in scrape_source):
    failures.append('scrape.py must reject source URL credentials before network reads')
for phrase in (
        'isinstance(timeout, bool)',
        'not isinstance(timeout, INTEGER_TYPES + (float,))',
        'timeout <= 0 or timeout != timeout',
        "timeout == float('inf')",
        "raise ValueError('timeout must be positive')"):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain finite positive timeout validation %r' % phrase)
for phrase in (
        "request.add_header('Accept-Encoding', 'identity')",
        'def header_values(self, headers, name):',
        'headers.get_all(name, [])',
        'headers.getheaders(name) or []',
        "declared_encodings = content_encoding.split(',')",
        "encoding.strip().lower() not in ('', 'identity')",
        "raise ValueError('response content encoding must be identity')"):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain content encoding boundary %r' % phrase)
if re.search(r"self\.header_values\(\s*headers,\s*'Content-Encoding'\)", scrape_source) is None:
    failures.append('scrape.py must retain shared content encoding header lookup')
encoding_check_index = scrape_source.find('headers = response.info()')
body_read_index = scrape_source.find('chunk = response.read(remaining)')
if (encoding_check_index >= 0 and body_read_index >= 0 and
        encoding_check_index > body_read_index):
    failures.append('scrape.py must reject non-identity content encoding before body reads')
for phrase in (
        "request.add_header('Accept', 'text/html, application/xhtml+xml')",
        "self.header_values(headers, 'Content-Type')",
        "content_type.split(';', 1)[0].strip().lower()",
        "media_type not in ('', 'text/html', 'application/xhtml+xml')",
        "raise ValueError('response content type must be HTML')"):
    if phrase not in scrape_source:
        failures.append('scrape.py must retain content type boundary %r' % phrase)
content_type_check_index = scrape_source.find(
    "self.header_values(headers, 'Content-Type')")
if (content_type_check_index >= 0 and body_read_index >= 0 and
        content_type_check_index > body_read_index):
    failures.append('scrape.py must reject explicit non-HTML content types before body reads')

test_source = read(os.path.join(ROOT, 'tests', 'test_scrape.py'))
for phrase in (
        'def test_main_preserves_validation_error_when_cleanup_fails(self):',
        'def test_main_closes_database_and_preserves_interruption(self):',
        'self.assertTrue(caught_error is primary_error)',
        'self.assertEqual(1, database.close_count)'):
    if phrase not in test_source:
        failures.append('tests/test_scrape.py must retain Product primary-error regression %r' % phrase)
for phrase in (
        'try:\n    import StringIO',
        'except ImportError:\n    import io as StringIO'):
    if phrase not in test_source:
        failures.append('tests/test_scrape.py must retain dual-runtime buffer fragment %r' % phrase)
if re.search(r'\b\d+[lL]\b', test_source):
    failures.append('tests/test_scrape.py must not contain Python-2-only long integer literals')
for test_name in (
        'test_read_accepts_body_at_configured_limit',
        'test_read_rejects_and_closes_oversized_body',
        'test_product_rejects_non_positive_response_limit',
        'test_product_rejects_non_integer_response_limit',
        'test_run_cli_forwards_response_limit'):
    if test_name not in test_source:
        failures.append('tests/test_scrape.py must retain %s' % test_name)
for test_name in (
        'test_product_rejects_non_string_source_urls_without_echoing_them',
        'test_normalized_link_rejects_non_string_values'):
    if test_name not in test_source:
        failures.append('tests/test_scrape.py must retain %s' % test_name)
for test_name in (
        'test_redirect_handler_has_explicit_hop_limits',
        'test_redirect_handler_allows_same_host_relative_redirect',
        'test_redirect_handler_allows_same_host_https_upgrade',
        'test_redirect_handler_rejects_unsafe_targets_without_echoing_them',
        'test_redirect_handler_closes_rejected_response_body'):
    if test_name not in test_source:
        failures.append('tests/test_scrape.py must retain %s' % test_name)
for phrase in (
        'class FakeRedirectResponse(object):',
        'self.assertEqual(1, redirect_response.close_count)'):
    if phrase not in test_source:
        failures.append('tests/test_scrape.py must retain rejected redirect cleanup coverage %r' % phrase)
if 'test_product_rejects_source_url_credentials_without_echoing_them' not in test_source:
    failures.append('tests/test_scrape.py must retain source URL credential rejection coverage')
if 'test_product_rejects_malformed_source_authorities_without_echoing_them' not in test_source:
    failures.append('tests/test_scrape.py must retain malformed source URL authority coverage')
for cleanup_test in (
        'test_main_closes_database_when_source_url_validation_fails',
        'test_main_closes_database_when_timeout_validation_fails',
        'test_main_closes_database_when_response_limit_validation_fails',
        'test_main_leaves_successful_cleanup_to_product_find'):
    if cleanup_test not in test_source:
        failures.append('tests/test_scrape.py must retain %s' % cleanup_test)
for constructor_cleanup_test in (
        'test_constructor_closes_connection_when_cursor_creation_fails',
        'test_constructor_preserves_cursor_failure_when_connection_close_fails',
        "self.assertEqual('cursor setup failed', str(error))",
        'self.assertEqual(1, connection.close_count)'):
    if constructor_cleanup_test not in test_source:
        failures.append('tests/test_scrape.py must retain constructor cleanup coverage %r' % (
            constructor_cleanup_test))
for timeout_test in (
        'test_product_accepts_positive_finite_timeout',
        'test_product_rejects_invalid_timeout_values',
        "float('nan')",
        "float('inf')",
        "float('-inf')"):
    if timeout_test not in test_source:
        failures.append('tests/test_scrape.py must retain timeout fixture %r' % timeout_test)
if 'test_find_products_skips_credential_bearing_links' not in test_source:
    failures.append('tests/test_scrape.py must retain product link credential rejection coverage')
if 'test_find_products_skips_malformed_links_and_continues' not in test_source:
    failures.append('tests/test_scrape.py must retain malformed product link continuation coverage')
for response_test in (
        'test_read_collects_fragmented_body_until_eof',
        'test_read_rejects_fragmented_body_over_configured_limit',
        'self.assertEqual([5, 3, 1], response.read_sizes)'):
    if response_test not in test_source:
        failures.append('tests/test_scrape.py must retain complete bounded response coverage %r' % response_test)
for response_test in (
        'test_build_request_requires_identity_content_encoding',
        'test_read_accepts_identity_content_encoding_variants',
        'test_read_rejects_compressed_response_before_body_read',
        'class LegacyFakeHeaders(object):',
        "self.assertEqual('identity', request.get_header('Accept-encoding'))",
        'self.assertEqual([], response.read_sizes)',
        "self.assertNotIn('gzip', str(error))"):
    if response_test not in test_source:
        failures.append('tests/test_scrape.py must retain content encoding coverage %r' % response_test)
for response_test in (
        'test_build_request_accepts_html_source_types',
        'test_read_accepts_html_content_type_variants',
        'test_read_rejects_non_html_content_type_before_body_read',
        'response.headers = headers_type(None, content_type)',
        "'text/html', 'application/json'",
        "'response content type must be HTML'"):
    if response_test not in test_source:
        failures.append('tests/test_scrape.py must retain content type coverage %r' % response_test)
content_type_rejection_test = re.search(
    r'def test_read_rejects_non_html_content_type_before_body_read\(self\):'
    r'[\s\S]*?(?=\n    def |\Z)',
    test_source,
)
if content_type_rejection_test is None:
    failures.append('tests/test_scrape.py must retain the non-HTML rejection test block')
else:
    for phrase in (
            "'text/html', 'application/json'",
            "'response content type must be HTML'",
            'self.assertEqual([], response.read_sizes)',
            'self.assertTrue(response.closed)'):
        if phrase not in content_type_rejection_test.group(0):
            failures.append('non-HTML rejection test must retain %r' % phrase)

link_scheme_plan = read(LINK_SCHEME_PLAN) if os.path.isfile(LINK_SCHEME_PLAN) else ''
if 'Status: Completed' not in link_scheme_plan or 'Product.normalized_link()' not in link_scheme_plan:
    failures.append('%s must record completed product link scheme work' % rel(LINK_SCHEME_PLAN))

cli_plan = read(CLI_DRY_RUN_PLAN) if os.path.isfile(CLI_DRY_RUN_PLAN) else ''
if 'Status: Completed' not in cli_plan or '--dry-run' not in cli_plan:
    failures.append('%s must record completed CLI dry-run work' % rel(CLI_DRY_RUN_PLAN))

security = read(os.path.join(ROOT, 'SECURITY.md'))
responsible_use = read(RESPONSIBLE_USE_GUIDE) if os.path.isfile(RESPONSIBLE_USE_GUIDE) else ''
responsible_use_prose = re.sub(r'<https?://[^>]+>', '', responsible_use)
responsible_use_contract = re.sub(r'\s+', ' ', responsible_use_prose.replace('`', '')).lower()
for phrase in (
        'obtain explicit written permission',
        'robots.txt is not authorization',
        'one request at a time',
        'retry-after',
        '429 or 503',
        'stop the run',
        'retention deadline',
        'delete raw responses',
        'do not collect personal data'):
    if phrase not in responsible_use_contract:
        failures.append('RESPONSIBLE_USE.md must retain %r' % phrase)
if '[`RESPONSIBLE_USE.md`](RESPONSIBLE_USE.md)' not in readme:
    failures.append('README.md must link the responsible-use guide')
if '`RESPONSIBLE_USE.md`' not in security:
    failures.append('SECURITY.md must link the responsible-use guide')
if 'Document target-site permission, rate limits, and data retention' in vision:
    failures.append('VISION.md must not retain the completed responsible-use priority')
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
if ('rejected redirect response bodies' not in readme or
        'Rejected redirect response bodies' not in security or
        'rejected redirect response bodies' not in changes.lower()):
    failures.append('docs must describe rejected redirect response body cleanup')
if 'Close rejected redirect response bodies' not in vision:
    failures.append('VISION.md must describe rejected redirect response body cleanup')
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
if any(re.search(r'malformed\s+source\s+URL\s+authorities', document, re.IGNORECASE) is None
       for document in (readme, vision, security, changes)):
    failures.append('docs must describe the malformed source URL authority boundary')
if any('non-string URL guard' not in document
       for document in (readme, vision, security, changes)):
    failures.append('docs must describe the non-string URL guard')
if 'all 65' not in readme:
    failures.append('README.md must record the complete 65-test offline suite')
if any('Scraper timeouts must be finite positive numbers before network setup.' not in document
       for document in (readme, vision, security, changes)):
    failures.append('docs must describe the finite positive timeout boundary')
for document_name, document in (
        ('README.md', readme),
        ('SECURITY.md', security),
        ('VISION.md', vision),
        ('CHANGES.md', changes)):
    if 'Python 2.7 and Python 3.12' not in document:
        failures.append('%s must document the Python 2.7 and Python 3.12 verification boundary' % document_name)
    if 'bounded response reads' not in document.lower():
        failures.append('%s must document complete bounded response reads' % document_name)
    if ('identity content encoding' not in document.lower() or
            'before body reads' not in document.lower()):
        failures.append('%s must document the content encoding boundary' % document_name)
    if 'explicit non-html content types' not in document.lower():
        failures.append('%s must document the content type boundary' % document_name)
    if 'product construction primary error' not in document.lower():
        failures.append('%s must document Product construction primary error preservation' % document_name)

agents = read(os.path.join(ROOT, 'AGENTS.md'))
if 'Python 2.7 and Python 3.12' not in agents or 'make check PYTHON=python3' not in agents:
    failures.append('AGENTS.md must document both runtime gates')
if 'identity content encoding' not in agents.lower() or 'before body reads' not in agents.lower():
    failures.append('AGENTS.md must document the content encoding boundary')
if 'explicit non-html content types' not in agents.lower():
    failures.append('AGENTS.md must document the content type boundary')

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

malformed_source_url_plan = read(MALFORMED_SOURCE_URL_PLAN) if os.path.isfile(MALFORMED_SOURCE_URL_PLAN) else ''
for evidence in (
        'Status: Completed',
        'repository and external-directory `make check` passed',
        'hostile malformed-source mutations were rejected',
        'generated-artifact and credential-pattern audits passed'):
    if evidence not in malformed_source_url_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(MALFORMED_SOURCE_URL_PLAN), evidence))

timeout_validation_plan = read(TIMEOUT_VALIDATION_PLAN) if os.path.isfile(TIMEOUT_VALIDATION_PLAN) else ''
for evidence in (
        'Status: Completed',
        'repository and external-directory `make check` passed',
        'hostile timeout mutations were rejected',
        'generated-artifact and credential-pattern audits passed'):
    if evidence not in timeout_validation_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(TIMEOUT_VALIDATION_PLAN), evidence))

redirect_rejection_cleanup_plan = read(REDIRECT_REJECTION_CLEANUP_PLAN) if os.path.isfile(
    REDIRECT_REJECTION_CLEANUP_PLAN
) else ''
for evidence in (
        'Status: Completed',
        '51 tests passed under Python 3',
        'make check PYTHON=python3 passed',
        'redirect response cleanup mutation was rejected',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in redirect_rejection_cleanup_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(REDIRECT_REJECTION_CLEANUP_PLAN), evidence))

python3_compatibility_plan = read(PYTHON3_COMPATIBILITY_PLAN) if os.path.isfile(PYTHON3_COMPATIBILITY_PLAN) else ''
for evidence in (
        'Status: Completed',
        '34 tests passed under Python 2.7 and Python 3.12',
        '21 workflow mutations were rejected under both runtimes',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile Python compatibility mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in python3_compatibility_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(PYTHON3_COMPATIBILITY_PLAN), evidence))

complete_bounded_read_plan = read(COMPLETE_BOUNDED_READ_PLAN) if os.path.isfile(COMPLETE_BOUNDED_READ_PLAN) else ''
for evidence in (
        'Status: Completed',
        '36 tests passed under Python 2.7 and Python 3.12',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile complete-read mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in complete_bounded_read_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(COMPLETE_BOUNDED_READ_PLAN), evidence))

content_encoding_plan = read(CONTENT_ENCODING_PLAN) if os.path.isfile(CONTENT_ENCODING_PLAN) else ''
for evidence in (
        'Status: Completed',
        '39 tests passed under Python 2.7 and Python 3.12',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile content-encoding mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in content_encoding_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(CONTENT_ENCODING_PLAN), evidence))

content_type_plan = read(CONTENT_TYPE_PLAN) if os.path.isfile(CONTENT_TYPE_PLAN) else ''
for evidence in (
        'Status: Completed',
        '42 tests passed under Python 2.7 and Python 3.12',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile content-type mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in content_type_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(CONTENT_TYPE_PLAN), evidence))

construction_cleanup_plan = read(CONSTRUCTION_CLEANUP_PLAN) if os.path.isfile(
    CONSTRUCTION_CLEANUP_PLAN
) else ''
for evidence in (
        'Status: Completed',
        '46 tests passed under Python 2.7 and Python 3.12',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile construction-cleanup mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in construction_cleanup_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(CONSTRUCTION_CLEANUP_PLAN), evidence))

database_constructor_cleanup_plan = read(DATABASE_CONSTRUCTOR_CLEANUP_PLAN) if os.path.isfile(
    DATABASE_CONSTRUCTOR_CLEANUP_PLAN
) else ''
for evidence in (
        'Status: Completed',
        '48 tests passed under Python 2.7 and Python 3.12',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile database-constructor cleanup mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in database_constructor_cleanup_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(DATABASE_CONSTRUCTOR_CLEANUP_PLAN), evidence))

product_construction_primary_error_plan = read(
    PRODUCT_CONSTRUCTION_PRIMARY_ERROR_PLAN
) if os.path.isfile(PRODUCT_CONSTRUCTION_PRIMARY_ERROR_PLAN) else ''
for evidence in (
        'Status: Completed',
        '50 tests passed under Python 2.7 and Python 3.12',
        'repository and external-directory `make check` passed under both runtimes',
        'hostile primary-error mutations were rejected',
        'generated-artifact and credential-pattern audits passed',
        'No live HTTP, HTML parsing, PostgreSQL, credentials, or deployment was exercised'):
    if evidence not in product_construction_primary_error_plan:
        failures.append('%s must record verification evidence %r' % (
            rel(PRODUCT_CONSTRUCTION_PRIMARY_ERROR_PLAN), evidence))

ci_plan = read(CI_PLAN) if os.path.isfile(CI_PLAN) else ''
if 'Status: Completed' not in ci_plan or 'make check' not in ci_plan:
    failures.append('%s must record completed CI baseline verification' % rel(CI_PLAN))

if failures:
    print('Documentation plan checks failed:\n- %s' % '\n- '.join(failures), file=sys.stderr)
    sys.exit(1)

print('Documentation plan checks passed')
