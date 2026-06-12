.PHONY: build check lint test verify

PYTHON ?= python2
PYTHON3 ?= python3
export PYTHONDONTWRITEBYTECODE = 1

lint:
	@if command -v $(PYTHON) >/dev/null 2>&1; then \
		$(PYTHON) -B -c 'compile(open("scrape.py").read(), "scrape.py", "exec")'; \
		$(PYTHON) -B scripts/check-docs-plans.py; \
	else \
		echo "$(PYTHON) unavailable; running Python 3 documentation-plan baseline only"; \
		$(PYTHON3) -B scripts/check-docs-plans.py; \
	fi

test:
	@if command -v $(PYTHON) >/dev/null 2>&1; then \
		$(PYTHON) -B -m unittest discover -s tests; \
	else \
		echo "$(PYTHON) unavailable; skipping legacy Python 2 tests"; \
	fi

build: lint

verify: lint test build

check: verify
