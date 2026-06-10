ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

PYTHON ?= python2
export PYTHONDONTWRITEBYTECODE = 1

.PHONY: build check lint test verify

lint:
	$(PYTHON) -B "$(ROOT)/scripts/check-docs-plans.py"
	cd "$(ROOT)" && $(PYTHON) -B -c 'compile(open("scrape.py").read(), "scrape.py", "exec")'

test:
	cd "$(ROOT)" && $(PYTHON) -B -m unittest discover -s tests

build: lint

verify: lint test

check: verify
