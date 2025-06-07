# SSH-MCP Tests

This directory contains tests for the SSH-MCP project.

## Running Tests

To run the tests, use pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest ssh_mcp/tests/test_config.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_config.py` - Tests for the configuration manager
- More tests will be added as the project develops

## Test Dependencies

The tests require:
- pytest
- mock/pytest-mock (for mocking SSH connections)

## Adding New Tests

When adding new tests:

1. Create a new file with a `test_` prefix
2. Use pytest fixtures for common setup
3. Follow the existing patterns for mocking external dependencies
