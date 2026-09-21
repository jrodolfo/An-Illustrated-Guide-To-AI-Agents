.DEFAULT_GOAL := help

PYTHON ?= python3
UV ?= uv
export PYTHONPATH := src

.PHONY: help test compile check sync tinyagent jupyter

help: ## Show available commands
	@echo "Available targets:"
	@echo
	@echo "  help       Show this help"
	@echo "  test       Run the unit tests"
	@echo "  compile    Compile Python source and tests"
	@echo "  check      Run all automated checks"
	@echo "  sync       Install notebook and terminal dependencies"
	@echo "  tinyagent  Start the TinyAgent CLI"
	@echo "  jupyter    Start JupyterLab"

test: ## Run the unit tests
	$(PYTHON) -m unittest discover -s tests -v

compile: ## Compile Python source and tests
	$(PYTHON) -m compileall -q src tests

check: test compile ## Run all automated checks

sync: ## Install notebook and terminal dependencies
	$(UV) sync --extra jupyter --extra terminal

tinyagent: ## Start the TinyAgent CLI
	$(UV) run --extra terminal tinyagent

jupyter: ## Start JupyterLab
	$(UV) run --extra jupyter jupyter lab
