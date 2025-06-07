#!/usr/bin/env python3
"""
SSH-MCP CLI tool.

This script provides a command-line interface for working with SSH-MCP.
"""
import argparse
import os
import sys
from typing import List, Optional

from ssh_mcp.config import ConfigurationManager
from ssh_mcp.executor import CommandExecutor
from ssh_mcp.server import SSHMCPServer


def run_server(args: argparse.Namespace) -> int:
    """
    Run the SSH-MCP server.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        server = SSHMCPServer(server_name=args.name, config_path=args.config)
        server.run()
        return 0

    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0

    except Exception as e:
        print(f"Error starting server: {str(e)}", file=sys.stderr)
        return 1


def run_command(args: argparse.Namespace) -> int:
    """
    Run a command on a remote server.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        config_manager = ConfigurationManager(args.config)
        executor = CommandExecutor(config_manager=config_manager)

        result = executor.execute_command(
            args.connection, args.remote_command, timeout=args.timeout
        )

        if result["stdout"]:
            print(result["stdout"], end="")

        if result["stderr"]:
            print(result["stderr"], end="", file=sys.stderr)

        if result["error"]:
            print(f"Error: {result['error']}", file=sys.stderr)

        return result["exit_code"]

    except Exception as e:
        print(f"Error executing command: {str(e)}", file=sys.stderr)
        return 1


def list_connections(args: argparse.Namespace) -> int:
    """
    List available connections.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        config_manager = ConfigurationManager(args.config)
        connections = config_manager.get_connection_names()

        print("Available connections:")
        for connection in connections:
            print(f"- {connection}")

        return 0

    except Exception as e:
        print(f"Error listing connections: {str(e)}", file=sys.stderr)
        return 1


def list_commands(args: argparse.Namespace) -> int:
    """
    List allowed commands.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        config_manager = ConfigurationManager(args.config)
        commands = config_manager.get_allowed_commands()

        print("Allowed commands:")
        for command in commands:
            print(f"- {command}")

        return 0

    except Exception as e:
        print(f"Error listing commands: {str(e)}", file=sys.stderr)
        return 1


def init_config(args: argparse.Namespace) -> int:
    """
    Initialize a configuration file.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        config_path = args.config

        if os.path.exists(config_path) and not args.force:
            print(f"Configuration file {config_path} already exists.")
            print("Use --force to overwrite it.")
            return 1

        # Create a new configuration manager (this will create a default config)
        config_manager = ConfigurationManager(config_path)

        print(f"Configuration file created at {config_path}")
        print("Edit this file to add your SSH connections.")
        return 0

    except Exception as e:
        print(f"Error initializing configuration: {str(e)}", file=sys.stderr)
        return 1


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

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server command
    server_parser = subparsers.add_parser(
        "server", help="Run the SSH-MCP server")
    server_parser.add_argument(
        "--name",
        help="Name of the MCP server (default: SSH-MCP Server)",
        default="SSH-MCP Server",
    )    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run a command on a remote server")
    run_parser.add_argument("connection", help="Name of the connection to use")
    run_parser.add_argument("remote_command", help="Command to execute")
    run_parser.add_argument(
        "--timeout",
        help="Command timeout in seconds (default: from config)",
        type=int,
        default=None,
    )

    # List connections command
    list_connections_parser = subparsers.add_parser(
        "list-connections", help="List available connections"
    )

    # List commands command
    list_commands_parser = subparsers.add_parser(
        "list-commands", help="List allowed commands"
    )    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a configuration file")
    init_parser.add_argument(
        "--force", help="Overwrite existing configuration file", action="store_true"
    )

    args = parser.parse_args()

    if args.command == "server":
        return run_server(args)
    elif args.command == "run":
        return run_command(args)
    elif args.command == "list-connections":
        return list_connections(args)
    elif args.command == "list-commands":
        return list_commands(args)
    elif args.command == "init":
        return init_config(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
