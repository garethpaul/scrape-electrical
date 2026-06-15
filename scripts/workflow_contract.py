from __future__ import print_function

import re


CHECKOUT_ACTION = 'actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10'
SETUP_PYTHON_ACTION = 'actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405'
CONTAINER_IMAGE = 'python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20'
CHECKOUT_BLOCK = '\n'.join((
    '      - name: Check out repository',
    '        uses: %s # v6.0.3' % CHECKOUT_ACTION,
    '        with:',
    '          persist-credentials: false',
))
SETUP_PYTHON_BLOCK = '\n'.join((
    '      - name: Set up Python',
    '        uses: %s # v6.2.0' % SETUP_PYTHON_ACTION,
    '        with:',
    '          python-version: "3.12"',
))


def validate(workflow):
    failures = []
    actions = re.findall(
        r'^[ \t]*(?:-[ \t]*)?uses:[ \t]*(\S+)(?:[ \t]+#.*)?$',
        workflow,
        re.MULTILINE,
    )

    if '  push:\n    branches:\n      - master' not in workflow:
        failures.append('validate pushes to master')
    if len(re.findall(r'^  pull_request:$', workflow, re.MULTILINE)) != 1:
        failures.append('validate pull requests exactly once')
    if len(re.findall(r'^  workflow_dispatch:$', workflow, re.MULTILINE)) != 1:
        failures.append('allow manual dispatch exactly once')
    if len(re.findall(r'^permissions:$', workflow, re.MULTILINE)) != 1:
        failures.append('declare workflow permissions exactly once')
    if not re.search(r'^permissions:\n  contents: read$', workflow, re.MULTILINE):
        failures.append('use read-only contents permission')
    if re.search(r'^[ \t]+[A-Za-z-]+:[ \t]+write[ \t]*$', workflow, re.MULTILINE):
        failures.append('not request write permissions')
    if len(re.findall(r'^  cancel-in-progress: true$', workflow, re.MULTILINE)) != 1:
        failures.append('cancel superseded runs exactly once')
    if len(re.findall(r'^  legacy-python:$', workflow, re.MULTILINE)) != 1:
        failures.append('define the legacy Python job exactly once')
    if len(re.findall(r'^  current-python:$', workflow, re.MULTILINE)) != 1:
        failures.append('define the current Python job exactly once')
    if len(re.findall(r'^    runs-on: ubuntu-24.04$', workflow, re.MULTILINE)) != 2:
        failures.append('use the fixed Ubuntu runner for both jobs')
    if len(re.findall(r'^    timeout-minutes: 10$', workflow, re.MULTILINE)) != 2:
        failures.append('bound both jobs to ten minutes')
    images = re.findall(r'^      image: (\S+)$', workflow, re.MULTILINE)
    if images != [CONTAINER_IMAGE]:
        failures.append('use one reviewed digest-pinned Python 2.7.18 image')
    if workflow.count(CHECKOUT_BLOCK) != 2:
        failures.append('use the exact credential-free checkout contract in both jobs')
    if SETUP_PYTHON_BLOCK not in workflow:
        failures.append('use the pinned Python 3.12 setup contract')
    if actions != [CHECKOUT_ACTION, CHECKOUT_ACTION, SETUP_PYTHON_ACTION]:
        failures.append('use only the reviewed checkout and setup-python actions')
    if workflow.count('persist-credentials:') != 2:
        failures.append('disable checkout credential persistence in both jobs')
    if len(re.findall(r'^        run: python2 --version$', workflow, re.MULTILINE)) != 1:
        failures.append('report the Python 2 runtime exactly once')
    if len(re.findall(r'^        run: python3 --version$', workflow, re.MULTILINE)) != 1:
        failures.append('report the Python 3 runtime exactly once')
    if len(re.findall(r'^        run: make check PYTHON=python2$', workflow, re.MULTILINE)) != 1:
        failures.append('run the canonical full gate once on Python 2')
    if len(re.findall(r'^        run: make check PYTHON=python3$', workflow, re.MULTILINE)) != 1:
        failures.append('run the canonical full gate once on Python 3')
    if 'continue-on-error' in workflow:
        failures.append('not allow offline scraper verification failures')
    if re.search(r'\b(?:pip|pip2|pip3) install\b', workflow):
        failures.append('not install live scraper or database dependencies')

    return failures
