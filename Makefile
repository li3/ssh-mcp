# SSH-MCP Makefile

.PHONY: all clean lint test test-unit test-integration dev install install-dev

# Python environment and tools
PYTHON = python
PYTEST = python -m pytest
BLACK = python -m black
ISORT = python -m isort
MYPY = python -m mypy

# Project paths
SRC_DIR = ssh_mcp
TEST_DIR = ssh_mcp/tests

all: lint test

# Development dependencies
install-dev:
	uv pip install -e ".[dev]"  

# Linting and formatting
lint: lint-black lint-isort lint-mypy

lint-black:
	$(BLACK) --check $(SRC_DIR)

lint-isort:
	$(ISORT) --check-only --profile black $(SRC_DIR)

lint-mypy:
	$(MYPY) $(SRC_DIR)

format:
	$(BLACK) $(SRC_DIR)
	$(ISORT) --profile black $(SRC_DIR)

# Testing
test: test-unit test-integration

test-unit:
	$(PYTEST) $(TEST_DIR) -v -k "not integration"

test-integration:
	$(PYTEST) $(TEST_DIR) -v -k "integration"

# Run server in development mode
dev:
	$(PYTHON) -m ssh_mcp --debug

# Clean up compiled Python files and caches
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name ".coverage.*" -delete
	rm -rf build/ dist/ *.egg-info/

# Install for production
install:
	uv pip install .
