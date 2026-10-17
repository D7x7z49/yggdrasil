# @path[Makefile]
# yggdrasil project tasks
# =======================
#
# common entry points for local development

.DEFAULT_GOAL := help

.PHONY: help setup install hooks lock lock-check agent-check check clean reset

# OVERVIEW
# --------
help:  ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

# SETUP
# -----
setup: hooks  ## install dependencies and git hooks

install:  ## install dependencies from the lockfile
	uv sync --locked

hooks: install  ## install the pre-commit git hooks
	uv run --locked pre-commit install --install-hooks

# LOCKFILE
# --------
lock:  ## update uv.lock
	uv lock

lock-check:  ## check that uv.lock is up to date
	uv lock --check

# VERIFICATION
# ------------
agent-check:  ## check the .agent directory layout
	uv run --locked python scripts/ci/check-agent-layout.py

check: lock-check  ## run the full local check
	uv run --locked pre-commit run --all-files --show-diff-on-failure

# CLEAN
# -----

# no build artifacts yet
clean:  ## remove build artifacts

# RESET
# -----
reset:  ## remove .venv and reinstall dependencies
	rm -rf .venv
	uv sync --locked
