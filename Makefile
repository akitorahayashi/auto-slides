# ==============================================================================
# Makefile for Project Automation
#
# Provides a unified interface for common development tasks, such as running
# the application, formatting code, and running tests.
#
# Inspired by the self-documenting Makefile pattern.
# See: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# ==============================================================================

# Default target when 'make' is run without arguments
.DEFAULT_GOAL := help

# Specify the Python executable and main Streamlit file name
PYTHON := ./.venv/bin/python
STREAMLIT_APP_FILE := ./src/main.py

# ==============================================================================
# HELP
# ==============================================================================

.PHONY: help
help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

.PHONY: setup
setup: ## Project initial setup: install dependencies
	@echo "🐍 Installing python dependencies with uv..."
	@uv sync
	@echo "✅ Dependencies installed."


# ==============================================================================
# APPLICATION
# ==============================================================================

.PHONY: run
run: ## Launch the Streamlit application with development port from secrets
	@echo "🚀 Starting Streamlit app on development port..."
	@DEV_PORT=$$(python -c "import streamlit as st; print(st.secrets.get('DEV_PORT', '8503'))"); \
	PYTHONPATH=. streamlit run $(STREAMLIT_APP_FILE) --server.port $$DEV_PORT
	
# ==============================================================================
# CODE QUALITY
# ==============================================================================

.PHONY: format
format: ## Automatically format code using Black and Ruff
	@echo "🎨 Formatting code with black and ruff..."
	@black .
	@ruff check . --fix

.PHONY: lint
lint: ## Perform static code analysis (check) using Black and Ruff
	@echo "🔬 Linting code with black and ruff..."
	@black --check .
	@ruff check .

# ==============================================================================
# TESTING
# ==============================================================================

.PHONY: test
test: unit-test ui-test intg-test e2e-test ## Run the full test suite

.PHONY: cov
cov: ## Run tests and generate coverage report
	@echo "📊 Generating test coverage report..."
	@PYTHONPATH=. $(PYTHON) -m pytest --cov=src --cov-report=html

.PHONY: unit-test
unit-test: ## Run unit tests
	@echo "Running unit tests..."
	@PYTHONPATH=. $(PYTHON) -m pytest tests/unit -s

.PHONY: ui-test
ui-test: ## Run UI tests
	@echo "Running UI tests..."
	@PYTHONPATH=. $(PYTHON) -m pytest tests/ui -s

.PHONY: intg-test
intg-test: ## Run integration tests
	@echo "Running integration tests..."
	@PYTHONPATH=. $(PYTHON) -m pytest tests/intg -v -s

.PHONY: e2e-test
e2e-test: ## Run end-to-end tests
	@echo "Running end-to-end tests..."
	@PYTHONPATH=. $(PYTHON) -m pytest tests/e2e -s

# ==============================================================================
# CLEANUP
# ==============================================================================

.PHONY: clean
clean: ## Remove __pycache__ and .venv to make project lightweight
	@echo "🧹 Cleaning up project..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .venv
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@echo "✅ Cleanup completed"