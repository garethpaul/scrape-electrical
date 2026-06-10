.PHONY: build check lint test verify

PYTHON ?= python2
CHECK_PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE = 1

lint:
	$(CHECK_PYTHON) -B scripts/check-docs-plans.py
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		$(PYTHON) -B -c 'compile(open("scrape.py").read(), "scrape.py", "exec")'; \
	else \
		echo "Skipping legacy Python 2 scraper syntax check: $(PYTHON) not found."; \
	fi

test:
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		$(PYTHON) -B -m unittest discover -s tests; \
	else \
		echo "Skipping legacy Python 2 scraper tests: $(PYTHON) not found."; \
	fi

build: lint

verify: lint test

check: verify
