#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS_PLANS = os.path.join(ROOT, 'docs', 'plans')
CANONICAL_PLAN = os.path.join(DOCS_PLANS, '2026-06-08-scrape-electrical-baseline.md')
LINK_SCHEME_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-product-link-scheme-guard.md')


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

plans = sorted(glob.glob(os.path.join(DOCS_PLANS, '*.md')))
if not plans:
    failures.append('docs/plans must contain at least one completed plan')

for plan_path in plans:
    plan = read(plan_path)
    if 'Status: Completed' not in plan or 'make check' not in plan:
        failures.append('%s must record completed status and make check verification' % rel(plan_path))

scrape_source = read(os.path.join(ROOT, 'scrape.py'))
if 'psycopg2.connect("user=%s password=%s host=%s dbname=%s"' in scrape_source:
    failures.append('scrape.py must not build a psycopg2 connection string by interpolation')
if 'psycopg2.connect(\n            user=self.dbuser,' not in scrape_source:
    failures.append('scrape.py must pass database connection fields as psycopg2 keyword arguments')
if 'from urlparse import urljoin, urlparse' not in scrape_source:
    failures.append('scrape.py must import Python 2 URL normalization helpers')
if 'def normalized_link(self, href):' not in scrape_source:
    failures.append('scrape.py must normalize parsed product links before database insertion')
if "parsed_url.scheme not in ('http', 'https')" not in scrape_source:
    failures.append('scrape.py must reject parsed product links that are not HTTP(S)')
if 'urljoin(self.url, href.strip())' not in scrape_source:
    failures.append('scrape.py must resolve relative product links against the source URL')

link_scheme_plan = read(LINK_SCHEME_PLAN) if os.path.isfile(LINK_SCHEME_PLAN) else ''
if 'Status: Completed' not in link_scheme_plan or 'Product.normalized_link()' not in link_scheme_plan:
    failures.append('%s must record completed product link scheme work' % rel(LINK_SCHEME_PLAN))

security = read(os.path.join(ROOT, 'SECURITY.md'))
if 'non-web link schemes' not in security or 'relative product links' not in security:
    failures.append('SECURITY.md must document product link scheme and relative URL boundaries')

if failures:
    print('Documentation plan checks failed:\n- %s' % '\n- '.join(failures), file=sys.stderr)
    sys.exit(1)

print('Documentation plan checks passed')
