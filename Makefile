.PHONY: build check lint test verify

PYTHON ?= python2
export PYTHONDONTWRITEBYTECODE = 1

lint:
	$(PYTHON) -B -c 'compile(open("scrape.py").read(), "scrape.py", "exec")'
	$(PYTHON) -B scripts/check-docs-plans.py

test:
	$(PYTHON) -B -m unittest discover -s tests

build: lint

verify: lint test build

check: verify
