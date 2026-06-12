from __future__ import print_function

import re


CHECKOUT_ACTION = 'actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10'
CONTAINER_IMAGE = 'python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20'
CHECKOUT_BLOCK = '\n'.join((
    '      - name: Check out repository',
    '        uses: %s # v6.0.3' % CHECKOUT_ACTION,
    '        with:',
    '          persist-credentials: false',
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
    if len(re.findall(r'^    runs-on: ubuntu-24.04$', workflow, re.MULTILINE)) != 1:
        failures.append('use the fixed Ubuntu runner exactly once')
    if len(re.findall(r'^    timeout-minutes: 10$', workflow, re.MULTILINE)) != 1:
        failures.append('bound the job to ten minutes exactly once')
    images = re.findall(r'^      image: (\S+)$', workflow, re.MULTILINE)
    if images != [CONTAINER_IMAGE]:
        failures.append('use one reviewed digest-pinned Python 2.7.18 image')
    if CHECKOUT_BLOCK not in workflow:
        failures.append('use the exact credential-free checkout contract')
    if actions != [CHECKOUT_ACTION]:
        failures.append('use only the reviewed checkout action')
    if workflow.count('persist-credentials:') != 1:
        failures.append('configure checkout credential persistence exactly once')
    if len(re.findall(r'^        run: python2 --version$', workflow, re.MULTILINE)) != 1:
        failures.append('report the Python 2 runtime exactly once')
    if len(re.findall(r'^        run: make check$', workflow, re.MULTILINE)) != 1:
        failures.append('run the canonical full gate exactly once')
    if 'continue-on-error' in workflow:
        failures.append('not allow offline scraper verification failures')
    if 'actions/setup-python' in workflow:
        failures.append('not replace full Python 2 verification with setup-python')
    if re.search(r'\b(?:pip|pip2|pip3) install\b', workflow):
        failures.append('not install live scraper or database dependencies')

    return failures
