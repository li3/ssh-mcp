"""
MCP server implementation for SSH-MCP.

This module provides the MCP server that exposes SSH command execution capabilities to LLMs.
"""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .config import ConfigurationManager
from .connection import SSHConnectionManager
from .executor import CommandExecutor


class SSHMCPServer:
    """MCP server for executing commands on remote servers via SSH."""

    def __init__(
        self, server_name: str = "SSH-MCP Server", config_path: Optional[str] = None
    ):
        """
        Initialize the MCP server.

        Args:
            server_name: The name of the MCP server.
            config_path: Optional path to the configuration file.
                        If not provided, the default ~/.ssh-mcp-config.yaml is used.
        """
        self.server_name = server_name
        self.config_manager = ConfigurationManager(config_path)
        self.connection_manager = SSHConnectionManager(self.config_manager)
        self.command_executor = CommandExecutor(
            self.connection_manager, self.config_manager
        )

        # Create the MCP server
        self.mcp = FastMCP(server_name)

        # Register resources and tools
        self._register_resources()
        self._register_tools()

    def _register_resources(self) -> None:
        """Register MCP resources."""

        @self.mcp.resource("ssh-mcp://connections")
        def get_connections() -> List[str]:
            """
            Get the list of available SSH connections.

            Returns:
                List of connection names.
            """
            return self.command_executor.get_connection_names()

        @self.mcp.resource("ssh-mcp://commands")
        def get_allowed_commands() -> List[str]:
            """
            Get the list of allowed commands.

            Returns:
                List of allowed command strings.
            """
            return self.command_executor.get_allowed_commands()

        @self.mcp.resource("ssh-mcp://configuration")
        def get_configuration() -> Dict[str, Any]:
            """
            Get the server configuration (without sensitive information).

            Returns:
                Dictionary containing server configuration.
            """
            # Create a sanitized version of the configuration
            sanitized_config = {
                "connections": {},
                "defaults": self.config_manager.config.get("defaults", {}),
            }

            # Add connection information without passwords
            for name, conn in self.config_manager.config.get("connections", {}).items():
                sanitized_conn = conn.copy()
                if "password" in sanitized_conn:
                    sanitized_conn["password"] = "********"
                sanitized_config["connections"][name] = sanitized_conn

            return sanitized_config

    def _register_tools(self) -> None:
        """Register MCP tools."""

        @self.mcp.tool()
        def execute_command(connection: str, command: str) -> Dict[str, Any]:
            """
            Execute a command on a remote server.

            Args:
                connection: The name of the connection to use.
                command: The command to execute.

            Returns:
                Dictionary containing the command execution results:
                {
                    "exit_code": int,
                    "stdout": str,
                    "stderr": str,
                    "success": bool,
                    "error": Optional[str]
                }
            """
            return self.command_executor.execute_command(connection, command)

        @self.mcp.tool()
        def list_connections() -> List[str]:
            """
            List available SSH connections.

            Returns:
                List of connection names.
            """
            return self.command_executor.get_connection_names()

        @self.mcp.tool()
        def list_allowed_commands() -> List[str]:
            """
            List allowed commands.

            Returns:
                List of allowed command strings.
            """
            return self.command_executor.get_allowed_commands()

    def run(self) -> None:
        """Run the MCP server."""
        self.mcp.run()


# Create a server instance if run directly
def create_server() -> SSHMCPServer:
    """
    Create an instance of the SSH-MCP server.

    Returns:
        SSHMCPServer instance.
    """
    return SSHMCPServer()


if __name__ == "__main__":
    server = create_server()
    server.run()
