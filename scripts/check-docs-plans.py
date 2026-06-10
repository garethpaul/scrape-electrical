#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS_PLANS = os.path.join(ROOT, 'docs', 'plans')
CANONICAL_PLAN = os.path.join(DOCS_PLANS, '2026-06-08-scrape-electrical-baseline.md')
LINK_SCHEME_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-product-link-scheme-guard.md')
CLI_DRY_RUN_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-cli-dry-run.md')
BYTECODE_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-bytecode-free-verification.md')
CI_PLAN = os.path.join(DOCS_PLANS, '2026-06-10-ci-baseline.md')
HOSTED_LEGACY_PLAN = os.path.join(DOCS_PLANS, '2026-06-10-hosted-legacy-validation.md')


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, 'r') as handle:
        return handle.read()


failures = []

if not os.path.isfile(CANONICAL_PLAN):
    failures.append('%s is missing' % rel(CANONICAL_PLAN))
if not os.path.isfile(LINK_SCHEME_PLAN):
    failures.append('%s is missing' % rel(LINK_SCHEME_PLAN))
if not os.path.isfile(CLI_DRY_RUN_PLAN):
    failures.append('%s is missing' % rel(CLI_DRY_RUN_PLAN))
if not os.path.isfile(BYTECODE_PLAN):
    failures.append('%s is missing' % rel(BYTECODE_PLAN))
if not os.path.isfile(CI_PLAN):
    failures.append('%s is missing' % rel(CI_PLAN))
if not os.path.isfile(HOSTED_LEGACY_PLAN):
    failures.append('%s is missing' % rel(HOSTED_LEGACY_PLAN))

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
    for filename in filenames:
        if filename.endswith(('.pyc', '.pyo')):
            bytecode_files.append(rel(os.path.join(dirpath, filename)))

if bytecode_files:
    failures.append('Python bytecode must not be present: %s' % ', '.join(sorted(bytecode_files)))

workflow_path = os.path.join(ROOT, '.github', 'workflows', 'check.yml')
workflow = read(workflow_path) if os.path.isfile(workflow_path) else ''
makefile = read(os.path.join(ROOT, 'Makefile'))
readme = read(os.path.join(ROOT, 'README.md'))
vision = read(os.path.join(ROOT, 'VISION.md'))
changes = read(os.path.join(ROOT, 'CHANGES.md'))
scrape_source = read(os.path.join(ROOT, 'scrape.py'))
required_workflow_phrases = (
    'runs-on: ubuntu-24.04',
    'actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10',
    'python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20',
    'permissions:',
    'contents: read',
    'timeout-minutes: 10',
    'workflow_dispatch:',
    'run: make check',
)
for phrase in required_workflow_phrases:
    if phrase not in workflow:
        failures.append('GitHub Actions workflow must contain %s' % phrase)
for line in workflow.splitlines():
    stripped = line.strip()
    if stripped.startswith('uses:'):
        revision = stripped.split('@', 1)[-1].split()[0]
        if len(revision) != 40 or any(character not in '0123456789abcdef' for character in revision):
            failures.append('GitHub Actions actions must be pinned to full commit SHAs')
            break
if 'continue-on-error' in workflow:
    failures.append('GitHub Actions must not allow legacy scraper verification failures')
required_makefile_phrases = (
    'ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))',
    'PYTHON ?= python2',
    '$(PYTHON) -B "$(ROOT)/scripts/check-docs-plans.py"',
    '$(PYTHON) -B -m unittest discover -s tests',
)
for phrase in required_makefile_phrases:
    if phrase not in makefile:
        failures.append('Makefile must contain %s' % phrase)
if 'command -v "$(PYTHON)"' in makefile or 'Skipping legacy Python 2' in makefile:
    failures.append('Makefile must require Python 2 scraper verification instead of skipping it')
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
