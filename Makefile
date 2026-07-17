# arvel-workflow — developer tasks. Gate targets mirror CI + `make check`.
RUN ?= uv run

.DEFAULT_GOAL := help
.PHONY: help sync lint format format-check typecheck imports test acceptance check pre-commit hooks clean

help:  ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

sync:  ## Create/refresh the dev environment (all extras + dev tools)
	uv sync --all-extras

lint:  ## Ruff lint
	$(RUN) ruff check .

format:  ## Ruff format (writes)
	$(RUN) ruff format .

format-check:  ## Ruff format (check only)
	$(RUN) ruff format --check .

typecheck:  ## Strict mypy + pyright (both, exactly as CI runs them)
	$(RUN) mypy src
	$(RUN) pyright

imports:  ## import-linter — keeps the engine (temporalio) off the import path
	PYTHONPATH=src $(RUN) lint-imports

test:  ## pytest — the pure logic (the engine is exercised by `make acceptance`)
	$(RUN) pytest

acceptance:  ## the real thing: boot the example app against a live Temporal dev server
	cd example && uv run python acceptance.py

check: lint format-check typecheck imports test  ## Everything CI runs

pre-commit:  ## Run all pre-commit hooks across the repo
	$(RUN) pre-commit run --all-files

hooks:  ## Install pre-commit git hooks
	$(RUN) pre-commit install

clean:  ## Remove caches + build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build **/__pycache__
