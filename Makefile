.PHONY: build check lint test verify

lint:
	python2 -m py_compile scrape.py
	python2 scripts/check-docs-plans.py

test:
	python2 -m unittest discover -s tests

build: lint

verify: lint test build

check: verify
