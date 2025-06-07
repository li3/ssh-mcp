"""
Command executor for SSH-MCP.

This module handles executing commands on remote servers and processing the results.
"""

import re
import shlex
from typing import Dict, List, Optional, Tuple, Any

from .config import ConfigurationManager
from .connection import SSHConnectionManager, SSHConnectionError


class CommandExecutionError(Exception):
    """Exception raised for command execution errors."""

    pass


class CommandExecutor:
    """Executes commands on remote servers and processes the results."""

    def __init__(
        self,
        connection_manager: Optional[SSHConnectionManager] = None,
        config_manager: Optional[ConfigurationManager] = None,
    ):
        """
        Initialize the command executor.

        Args:
            connection_manager: Optional SSHConnectionManager instance.
                               If not provided, a new one will be created.
            config_manager: Optional ConfigurationManager instance.
                           If not provided, a new one will be created.
        """
        self.config_manager = config_manager or ConfigurationManager()
        self.connection_manager = connection_manager or SSHConnectionManager(
            self.config_manager
        )
        self.allowed_commands = self.config_manager.get_allowed_commands()
        self.max_output_size = self.config_manager.get_max_output_size()

    def execute_command(
        self, connection_name: str, command: str, timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on a remote server.

        Args:
            connection_name: The name of the connection from the configuration.
            command: The command to execute.
            timeout: Optional timeout for the command execution in seconds.
                    If not provided, the default timeout from the configuration is used.

        Returns:
            Dict containing the command execution results:
            {
                "exit_code": int,
                "stdout": str,
                "stderr": str,
                "success": bool,
                "error": Optional[str]
            }

        Raises:
            CommandExecutionError: If the command is not allowed or execution fails.
        """
        # Validate the command
        self._validate_command(command)

        try:
            # Get the connection
            connection = self.connection_manager.get_connection(connection_name)

            # Execute the command
            exit_code, stdout, stderr = connection.execute_command(
                command, timeout=timeout or self.config_manager.get_timeout()
            )

            # Truncate output if it exceeds the maximum size
            if len(stdout) > self.max_output_size:
                stdout = stdout[: self.max_output_size] + "\n... (output truncated)"

            if len(stderr) > self.max_output_size:
                stderr = stderr[: self.max_output_size] + "\n... (output truncated)"

            return {
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "success": exit_code == 0,
                "error": None,
            }

        except SSHConnectionError as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "success": False,
                "error": str(e),
            }

        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "success": False,
                "error": f"Command execution failed: {str(e)}",
            }

    def _validate_command(self, command: str) -> None:
        """
        Validate that a command is allowed to be executed.

        Args:
            command: The command to validate.

        Raises:
            CommandExecutionError: If the command is not allowed.
        """
        # Parse the command to get the base command
        try:
            args = shlex.split(command)
            if not args:
                raise CommandExecutionError("Empty command")

            base_command = args[0]
        except Exception as e:
            raise CommandExecutionError(f"Invalid command format: {str(e)}")

        # Check if the base command is in the allowed list
        if base_command not in self.allowed_commands:
            raise CommandExecutionError(
                f"Command '{base_command}' is not allowed. "
                f"Allowed commands are: {', '.join(self.allowed_commands)}"
            )

    def get_connection_names(self) -> List[str]:
        """
        Get the list of available connection names.

        Returns:
            List of connection name strings.
        """
        return self.config_manager.get_connection_names()

    def get_allowed_commands(self) -> List[str]:
        """
        Get the list of allowed commands.

        Returns:
            List of allowed command strings.
        """
        return self.allowed_commands
