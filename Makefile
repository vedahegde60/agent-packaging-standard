# Top-level Makefile
# Usage:
#   make test-release       # run full pre-release smoke (tests + e2e)
#   make test               # just pytest (fast)
#   make clean              # remove temp build artifacts
#   make dev-install        # pip install -e cli -e registry (current venv)

.PHONY: test-release test clean dev-install

# You can override PY?=python3 if needed, e.g. PY=python
PY ?= python3

test-release:
	@bash scripts/test_release.sh

test:
	@$(PY) -m pytest -q

dev-install:
	@$(PY) -m pip install -U pip
	@$(PY) -m pip install -e cli/ -e registry/ -r examples/echo-agent/requirements.txt || true

clean:
	@rm -rf dist .pytest_cache .coverage build
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} +

