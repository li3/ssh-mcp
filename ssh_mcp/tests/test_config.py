"""
Tests for the configuration manager.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from ssh_mcp.config import ConfigurationManager


@pytest.fixture
def sample_config():
    """Fixture providing a sample configuration dictionary."""
    return {
        "connections": {
            "test-server": {
                "hostname": "test.example.com",
                "port": 2222,
                "username": "testuser",
                "auth_method": "key",
                "key_path": "~/.ssh/id_test",
            },
            "password-server": {
                "hostname": "password.example.com",
                "username": "passuser",
                "auth_method": "password",
                "password": "testpassword",
            },
        },
        "defaults": {
            "timeout": 45,
            "max_output_size": 2048,
            "allowed_commands": ["ls", "cat", "echo"],
        },
    }


@pytest.fixture
def config_file(sample_config):
    """Fixture creating a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        yaml.dump(sample_config, f)
        temp_path = f.name

    yield temp_path

    # Clean up the temporary file
    os.unlink(temp_path)


def test_load_config(config_file, sample_config):
    """Test loading configuration from a file."""
    config_manager = ConfigurationManager(config_file)

    # Test that the configuration was loaded correctly
    assert "connections" in config_manager.config
    assert "test-server" in config_manager.config["connections"]
    assert "password-server" in config_manager.config["connections"]

    # Test connection details
    test_server = config_manager.get_connection_config("test-server")
    assert test_server["hostname"] == "test.example.com"
    assert test_server["port"] == 2222
    assert test_server["username"] == "testuser"
    assert test_server["auth_method"] == "key"

    # Test defaults
    assert config_manager.get_timeout() == 45
    assert config_manager.get_max_output_size() == 2048
    assert "ls" in config_manager.get_allowed_commands()
    assert "cat" in config_manager.get_allowed_commands()
    assert "echo" in config_manager.get_allowed_commands()


def test_get_connection_names(config_file):
    """Test getting connection names."""
    config_manager = ConfigurationManager(config_file)
    names = config_manager.get_connection_names()

    assert "test-server" in names
    assert "password-server" in names
    assert len(names) == 2


def test_nonexistent_connection(config_file):
    """Test getting a nonexistent connection."""
    config_manager = ConfigurationManager(config_file)

    with pytest.raises(ValueError):
        config_manager.get_connection_config("nonexistent-server")


def test_create_default_config():
    """Test creating a default configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a path to a nonexistent file
        config_path = os.path.join(temp_dir, "config.yaml")

        # Create a configuration manager pointing to the nonexistent file
        config_manager = ConfigurationManager(config_path)

        # The file should now exist
        assert os.path.exists(config_path)

        # The config should have default values
        assert "connections" in config_manager.config
        assert "defaults" in config_manager.config
        assert "allowed_commands" in config_manager.config["defaults"]
