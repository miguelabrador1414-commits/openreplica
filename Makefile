PY ?= python3

.PHONY: check test compile lint fmt install clean

check: compile test lint

compile:
	$(PY) -m compileall -q tools tests

test:
	$(PY) -m unittest discover -s tests -v

lint:
	@command -v ruff >/dev/null 2>&1 && ruff check . || echo "ruff not installed; skipping"

fmt:
	@command -v ruff >/dev/null 2>&1 && ruff format . || echo "ruff not installed; skipping"

install:
	./scripts/install.sh --global

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache
