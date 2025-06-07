# MCP Server Quickstart

This document summarizes the minimal steps and commands to create and run an MCP server using the Python SDK.

## Core Concepts

*   **Server (`FastMCP`)**: The main interface for the MCP protocol. Handles connections, protocol compliance, and message routing.
*   **Resources (`@mcp.resource`)**: Expose data to LLMs (like GET endpoints). Should not perform significant computation or have side effects.
*   **Tools (`@mcp.tool`)**: Allow LLMs to take actions (like POST endpoints). Expected to perform computation and have side effects.
*   **Prompts (`@mcp.prompt`)**: Reusable templates for LLM interactions.

## Minimal Server (`server.py`)

```python
from mcp.server.fastmcp import FastMCP

# 1. Create an MCP server instance
mcp = FastMCP("MyDemoServer")

# 2. Define a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

# 3. Define a resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Provides a personalized greeting."""
    return f"Hello, {name}!"

# 4. (Optional) Run directly if script is executed
if __name__ == "__main__":
    mcp.run()
```

## Installation and Setup

We recommend using `uv` for project management.

1.  **Initialize a new project (if you don't have one):**
    ```bash
    uv init my-mcp-server
    cd my-mcp-server
    ```

2.  **Add MCP to your project dependencies:**
    ```bash
    uv add "mcp[cli]"
    ```
    Alternatively, using pip:
    ```bash
    pip install "mcp[cli]"
    ```

## Running the Server

### Development Mode (with MCP Inspector)

This is the fastest way to test and debug.

```bash
mcp dev server.py
```

You can also specify dependencies or mount local code:

```bash
# Add dependencies
mcp dev server.py --with pandas --with numpy

# Mount local code
mcp dev server.py --with-editable .
```

### Direct Execution

If your `server.py` includes `if __name__ == "__main__": mcp.run()`, you can run it as a standard Python script:

```bash
python server.py
```

Alternatively, use the `mcp run` command:

```bash
mcp run server.py
```
**Note:** `mcp run` and `mcp dev` are designed for `FastMCP` implementations, not the low-level server variant.

## Key Commands Summary

*   **Initialize project:** `uv init <project-name>`
*   **Add MCP SDK:** `uv add "mcp[cli]"` or `pip install "mcp[cli]"`
