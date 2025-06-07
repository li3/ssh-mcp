# uv Command Reference

This document summarizes basic `uv` commands for project management.

## Project Setup

### `uv init`

Initializes a new Python project managed by `uv`. This command helps set up the basic project structure and configuration for `uv`.

**Basic Usage:**
```bash
uv init
```

This command will typically create or update `pyproject.toml` to make the project compatible with `uv` and set up a virtual environment.

## Managing Dependencies

### `uv add`

Adds one or more packages as dependencies to your project. It updates your `pyproject.toml` file and installs the packages.

**Basic Usage:**
```bash
uv add <package_name>
```

**Example:**
```bash
uv add requests
```

To add a specific version:
```bash
uv add "requests>=2.0"
```

To add a development dependency:
```bash
uv add --dev <package_name>
```

**Example:**
```bash
uv add --dev pytest
```

### `uv remove`

Removes one or more packages from your project's dependencies. It updates your `pyproject.toml` file and uninstalls the packages.

**Basic Usage:**
```bash
uv remove <package_name>
```

**Example:**
```bash
uv remove requests
```

To remove a development dependency:
```bash
uv remove --dev <package_name>
```

**Example:**
```bash
uv remove --dev pytest
```

---
*Source: [uv CLI Reference](https://docs.astral.sh/uv/reference/cli/)*
