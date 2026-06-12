#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
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
required_makefile_phrases = (
    'ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))',
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

readme = read(os.path.join(ROOT, 'README.md'))
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

ci_plan = read(CI_PLAN) if os.path.isfile(CI_PLAN) else ''
if 'Status: Completed' not in ci_plan or 'make check' not in ci_plan:
    failures.append('%s must record completed CI baseline verification' % rel(CI_PLAN))

if failures:
    print('Documentation plan checks failed:\n- %s' % '\n- '.join(failures), file=sys.stderr)
    sys.exit(1)

print('Documentation plan checks passed')
