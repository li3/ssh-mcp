"""
SSH connection manager for SSH-MCP.

This module handles establishing and managing SSH connections to remote servers.
"""

import io
import socket
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import paramiko

from .config import ConfigurationManager


class SSHConnectionError(Exception):
    """Exception raised for SSH connection errors."""

    pass


class SSHConnection:
    """Manages a single SSH connection to a remote server."""

    def __init__(self, config: Dict[str, Any], timeout: int = 30):
        """
        Initialize an SSH connection.

        Args:
            config: Dictionary containing connection configuration.
            timeout: Connection timeout in seconds.

        Raises:
            SSHConnectionError: If the connection cannot be established.
        """
        self.config = config
        self.timeout = timeout
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False

    def connect(self) -> None:
        """
        Establish the SSH connection.

        Raises:
            SSHConnectionError: If the connection cannot be established.
        """
        try:
            connect_kwargs = {
                "hostname": self.config["hostname"],
                "port": self.config.get("port", 22),
                "username": self.config["username"],
                "timeout": self.timeout,
            }

            if self.config["auth_method"] == "password":
                connect_kwargs["password"] = self.config["password"]
            else:  # key-based authentication
                key_path = self.config.get("key_path")
                if key_path:
                    connect_kwargs["key_filename"] = key_path

            self.client.connect(**connect_kwargs)
            self.connected = True

        except (
            paramiko.AuthenticationException,
            paramiko.SSHException,
            socket.error,
        ) as e:
            raise SSHConnectionError(
                f"Failed to connect to {self.config['hostname']}: {str(e)}"
            )

    def disconnect(self) -> None:
        """Close the SSH connection."""
        if self.connected:
            self.client.close()
            self.connected = False

    def execute_command(
        self, command: str, timeout: Optional[int] = None
    ) -> Tuple[int, str, str]:
        """
        Execute a command on the remote server.

        Args:
            command: The command to execute.
            timeout: Command execution timeout in seconds. If None, uses the default timeout.

        Returns:
            Tuple of (exit_code, stdout, stderr).

        Raises:
            SSHConnectionError: If the command execution fails.
        """
        if not self.connected:
            self.connect()

        cmd_timeout = timeout or self.timeout

        try:
            # Execute the command
            stdin, stdout, stderr = self.client.exec_command(
                command, timeout=cmd_timeout
            )

            # Read output with a shorter timeout
            stdout_str = ""
            stderr_str = ""

            # Set a shorter channel timeout for reading
            stdout.channel.settimeout(5.0)
            stderr.channel.settimeout(5.0)

            try:
                stdout_str = stdout.read().decode("utf-8")
            except socket.timeout:
                # If we timeout, we'll use what we have so far
                pass

            try:
                stderr_str = stderr.read().decode("utf-8")
            except socket.timeout:
                # If we timeout, we'll use what we have so far
                pass

            # Get exit code (with a timeout)
            exit_code = 0
            try:
                # Set a short timeout for getting the exit status
                stdout.channel.settimeout(2.0)
                exit_code = stdout.channel.recv_exit_status()
            except socket.timeout:
                # If we timeout waiting for the exit code, assume it's 0
                # if we got stdout and no stderr
                if stdout_str and not stderr_str:
                    exit_code = 0
                else:
                    exit_code = -1

            return exit_code, stdout_str, stderr_str

        except (paramiko.SSHException, socket.error, socket.timeout) as e:
            raise SSHConnectionError(f"Command execution failed: {str(e)}")


class SSHConnectionManager:
    """Manages multiple SSH connections."""

    def __init__(self, config_manager: ConfigurationManager):
        """
        Initialize the SSH connection manager.

        Args:
            config_manager: The configuration manager.
        """
        self.config_manager = config_manager
        self.connections: Dict[str, SSHConnection] = {}
        self.last_used: Dict[str, float] = {}

    def get_connection(self, connection_name: str) -> SSHConnection:
        """
        Get an SSH connection by name.

        Args:
            connection_name: The name of the connection.

        Returns:
            The SSH connection.

        Raises:
            ValueError: If the connection name is not found in the configuration.
            SSHConnectionError: If the connection cannot be established.
        """
        # Get connection if it already exists
        if connection_name in self.connections:
            # Update the last_used time
            self.last_used[connection_name] = time.time()
            return self.connections[connection_name]

        # Get connection configuration
        connection_config = self.config_manager.get_connection_config(connection_name)

        # Create a new connection
        connection = SSHConnection(
            connection_config, timeout=self.config_manager.get_timeout()
        )
        connection.connect()

        # Store the connection
        self.connections[connection_name] = connection
        self.last_used[connection_name] = time.time()

        return connection

    def close_connection(self, connection_name: str) -> None:
        """
        Close an SSH connection by name.

        Args:
            connection_name: The name of the connection.
        """
        if connection_name in self.connections:
            self.connections[connection_name].disconnect()
            del self.connections[connection_name]
            if connection_name in self.last_used:
                del self.last_used[connection_name]

    def close_all_connections(self) -> None:
        """Close all SSH connections."""
        for connection_name in list(self.connections.keys()):
            self.close_connection(connection_name)

    def _cleanup_connections(self, max_idle_time: int = 300) -> None:
        """
        Clean up idle connections.

        Args:
            max_idle_time: Maximum idle time in seconds before a connection is closed.
        """
        current_time = time.time()
        for connection_name in list(self.last_used.keys()):
            if current_time - self.last_used[connection_name] > max_idle_time:
                self.close_connection(connection_name)
