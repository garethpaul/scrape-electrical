#!/usr/bin/env python2
from __future__ import print_function

from workflow_contract import (
    CHECKOUT_ACTION,
    CONTAINER_IMAGE,
    SETUP_PYTHON_ACTION,
    validate,
)


BASELINE = '''name: Check

on:
  pull_request:
  push:
    branches:
      - master
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  legacy-python:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    container:
      image: python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Show Python runtime
        run: python2 --version
      - name: Run full offline scraper verification
        run: make check PYTHON=python2

  current-python:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: "3.12"
      - name: Show Python runtime
        run: python3 --version
      - name: Run full offline scraper verification
        run: make check PYTHON=python3
'''


def mutate(description, target, replacement):
    mutated = BASELINE.replace(target, replacement, 1)
    if mutated == BASELINE:
        raise AssertionError('%s mutation did not alter the fixture' % description)
    return mutated


def assert_invalid(description, workflow):
    if not validate(workflow):
        raise AssertionError('%s mutation was accepted' % description)


if validate(BASELINE):
    raise AssertionError('baseline workflow is invalid: %s' % ', '.join(validate(BASELINE)))

mutations = {
    'contradictory credentials': mutate('contradictory credentials', 'persist-credentials: false', 'persist-credentials: false\n          persist-credentials: true'),
    'relocated credentials': mutate('relocated credentials', '        with:\n          persist-credentials: false\n', '').replace('permissions:', 'persist-credentials: false\n\npermissions:', 1),
    'floating checkout action': mutate('floating checkout action', CHECKOUT_ACTION, 'actions/checkout@v6'),
    'extra action': mutate('extra action', '      - name: Show Python runtime', '      - uses: example/unreviewed-action@v1\n      - name: Show Python runtime'),
    'write permission': mutate('write permission', 'contents: read', 'contents: read\n  issues: write'),
    'missing push': mutate('missing push', '  push:\n    branches:\n      - master\n', ''),
    'missing pull request': mutate('missing pull request', '  pull_request:\n', ''),
    'missing manual dispatch': mutate('missing manual dispatch', '  workflow_dispatch:\n', ''),
    'missing current job': mutate('missing current job', '  current-python:', '  current-runtime:'),
    'duplicate runner': mutate('duplicate runner', '    runs-on: ubuntu-24.04', '    runs-on: ubuntu-24.04\n    runs-on: ubuntu-24.04'),
    'unbounded job': mutate('unbounded job', '    timeout-minutes: 10\n', ''),
    'floating container': mutate('floating container', CONTAINER_IMAGE, 'python:2.7.18'),
    'wrong container digest': mutate('wrong container digest', 'c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20', '0000000000000000000000000000000000000000000000000000000000000000'),
    'continued failure': mutate('continued failure', '    steps:', '    continue-on-error: true\n    steps:'),
    'skipped legacy runtime proof': mutate('skipped legacy runtime proof', 'run: python2 --version', 'run: true'),
    'skipped current runtime proof': mutate('skipped current runtime proof', 'run: python3 --version', 'run: true'),
    'weakened legacy gate': mutate('weakened legacy gate', 'run: make check PYTHON=python2', 'run: make lint PYTHON=python2'),
    'weakened current gate': mutate('weakened current gate', 'run: make check PYTHON=python3', 'run: make lint PYTHON=python3'),
    'floating setup-python': mutate('floating setup-python', SETUP_PYTHON_ACTION, 'actions/setup-python@v6'),
    'wrong Python version': mutate('wrong Python version', 'python-version: "3.12"', 'python-version: "3.11"'),
    'dependency installation': mutate('dependency installation', 'run: make check PYTHON=python3', 'run: pip install -r requirements.txt && make check PYTHON=python3'),
}

for description, workflow in mutations.items():
    assert_invalid(description, workflow)

print('workflow contract tests passed (%d mutations rejected).' % len(mutations))
