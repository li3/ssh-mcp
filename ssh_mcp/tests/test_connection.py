"""
Tests for the SSH connection module.
"""

import os
import socket
import tempfile
import time
from pathlib import Path

import paramiko
import pytest
import yaml

from ssh_mcp.config import ConfigurationManager
from ssh_mcp.connection import SSHConnection, SSHConnectionError, SSHConnectionManager
from ssh_mcp.tests.mock_ssh_server import MockSSHServer


@pytest.fixture(scope="module")
def mock_ssh_server():
    """Fixture providing a mock SSH server."""
    # Start the mock SSH server
    server = MockSSHServer(port=2222)
    server.start()

    # Wait a bit for the server to start
    time.sleep(0.5)

    yield server

    # Stop the server
    server.stop()


@pytest.fixture
def ssh_config(mock_ssh_server):
    """Fixture providing SSH connection configuration."""
    return {
        "hostname": "127.0.0.1",
        "port": mock_ssh_server.port,
        "username": "testuser",
        "auth_method": "password",
        "password": "testpass",
    }


@pytest.fixture
def config_file(ssh_config):
    """Fixture creating a temporary configuration file with SSH connection details."""
    config = {
        "connections": {"test-server": ssh_config},
        "defaults": {
            "timeout": 5,
            "max_output_size": 1024,
            "allowed_commands": ["ls", "cat", "echo"],
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        yaml.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Clean up the temporary file
    os.unlink(temp_path)


def test_ssh_connection_init(ssh_config):
    """Test initializing an SSH connection."""
    connection = SSHConnection(ssh_config)
    assert connection.config == ssh_config
    assert connection.timeout == 30  # Default timeout
    assert not connection.connected


def test_ssh_connection_connect(ssh_config, mock_ssh_server):
    """Test connecting to an SSH server."""
    connection = SSHConnection(ssh_config)

    # Connect to the server
    connection.connect()
    assert connection.connected

    # Disconnect
    connection.disconnect()
    assert not connection.connected


def test_ssh_connection_execute_command(ssh_config, mock_ssh_server):
    """Test executing a command over SSH."""
    connection = SSHConnection(ssh_config)

    # Connect to the server
    connection.connect()

    # Execute a simple echo command
    exit_code, stdout, stderr = connection.execute_command("echo hello")

    # Check the results - be pragmatic about what we test
    assert isinstance(exit_code, int)
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)
    assert exit_code == 0
    assert "hello" in stdout

    # Disconnect
    connection.disconnect()


def test_ssh_connection_execute_invalid_command(ssh_config, mock_ssh_server):
    """Test executing an invalid command over SSH."""
    connection = SSHConnection(ssh_config)

    # Connect to the server
    connection.connect()  # Execute an invalid command - focus on the basic behavior
    exit_code, stdout, stderr = connection.execute_command("invalid_command")

    # Check the results - be pragmatic
    assert isinstance(exit_code, int)
    assert exit_code != 0  # Should be non-zero for error
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)

    # Disconnect
    connection.disconnect()


def test_ssh_connection_manager(config_file, mock_ssh_server):
    """Test the SSH connection manager."""
    config_manager = ConfigurationManager(config_file)
    connection_manager = SSHConnectionManager(config_manager)

    # Get a connection
    connection = connection_manager.get_connection("test-server")
    assert connection.connected  # Execute a command
    exit_code, stdout, stderr = connection.execute_command("echo hello world")

    # Check the results - be pragmatic about exact output format
    assert isinstance(exit_code, int)
    assert exit_code == 0
    assert isinstance(stdout, str)
    assert "hello world" in stdout
    assert isinstance(stderr, str)

    # Close all connections
    connection_manager.close_all_connections()
    assert not connection.connected


def test_ssh_connection_error():
    """Test SSH connection error handling."""
    # Create a configuration with an invalid hostname
    config = {
        "hostname": "nonexistent-host.example.com",
        "port": 22,
        "username": "testuser",
        "auth_method": "password",
        "password": "testpass",
    }

    connection = SSHConnection(config, timeout=1)

    # Attempt to connect should raise an exception
    with pytest.raises(SSHConnectionError):
        connection.connect()


def test_ssh_connection_manager_cleanup(config_file, mock_ssh_server):
    """Test SSH connection manager cleanup of idle connections."""
    config_manager = ConfigurationManager(config_file)
    connection_manager = SSHConnectionManager(config_manager)

    # Get a connection
    connection = connection_manager.get_connection("test-server")
    assert connection.connected

    # Override the last_used time to simulate an idle connection
    # 10 minutes ago
    connection_manager.last_used["test-server"] = time.time() - 600

    # Trigger cleanup (max_idle_time=1 second)
    connection_manager._cleanup_connections(max_idle_time=1)

    # The connection should be closed and removed
    assert "test-server" not in connection_manager.connections
    assert "test-server" not in connection_manager.last_used
