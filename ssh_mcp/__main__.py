"""
Main entry point for SSH-MCP.

This module provides a simple command-line interface to run the SSH-MCP server.
"""

import argparse
import os
import sys
from typing import Optional

from .server import SSHMCPServer


def main() -> int:
    """
    Main entry point for the SSH-MCP CLI.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = argparse.ArgumentParser(
        description="SSH-MCP: MCP server for SSH command execution"
    )
    parser.add_argument(
        "--config",
        help="Path to the configuration file (default: ~/.ssh-mcp-config.yaml)",
        default=os.path.expanduser("~/.ssh-mcp-config.yaml"),
    )
    parser.add_argument(
        "--name",
        help="Name of the MCP server (default: SSH-MCP Server)",
        default="SSH-MCP Server",
    )

    args = parser.parse_args()

    try:
        # Create and run the server
        server = SSHMCPServer(server_name=args.name, config_path=args.config)
        server.run()
        return 0

    except Exception as e:
        print(f"Error starting SSH-MCP server: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
