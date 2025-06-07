"""
Configuration manager for SSH-MCP.

This module handles loading and validating configuration from ~/.ssh-mcp-config.yaml.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml


class ConfigurationManager:
    """Manages SSH-MCP configuration from ~/.ssh-mcp-config.yaml."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Optional path to the configuration file.
                         If not provided, defaults to ~/.ssh-mcp-config.yaml.
        """
        self.config_path = config_path or os.path.expanduser("~/.ssh-mcp-config.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the config file.

        Returns:
            Dict containing the configuration.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            yaml.YAMLError: If the configuration file is invalid YAML.
        """
        config_file = Path(self.config_path)

        if not config_file.exists():
            # Create default configuration if not present
            default_config = self._create_default_config()
            with open(config_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)
            return default_config

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Process environment variables in the config
        config = self._process_env_vars(config)

        # Validate the configuration
        self._validate_config(config)

        return config

    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create a default configuration.

        Returns:
            Dict containing the default configuration.
        """
        return {
            "connections": {
                "example": {
                    "hostname": "example.com",
                    "port": 22,
                    "username": "user",
                    "auth_method": "key",
                    "key_path": os.path.expanduser("~/.ssh/id_rsa"),
                }
            },
            "defaults": {
                "timeout": 30,
                "max_output_size": 1048576,  # 1MB
                "allowed_commands": [
                    "ls",
                    "cat",
                    "grep",
                    "find",
                    "ps",
                    "top",
                    "df",
                    "du",
                    "free",
                ],
            },
        }

    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process environment variables in the configuration.

        Args:
            config: The configuration dict.

        Returns:
            Dict with environment variables replaced.
        """
        # Convert the config to a string
        config_str = yaml.dump(config)

        # Replace environment variables (${VAR_NAME})
        pattern = r"\${([A-Za-z0-9_]+)}"

        def replace_env_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, f"${{{var_name}}}")

        config_str = re.sub(pattern, replace_env_var, config_str)

        # Convert back to a dict
        return yaml.safe_load(config_str)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate the configuration.

        Args:
            config: The configuration dict to validate.

        Raises:
            ValueError: If the configuration is invalid.
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        if "connections" not in config:
            raise ValueError("Configuration must contain a 'connections' section")

        if not isinstance(config["connections"], dict):
            raise ValueError("'connections' section must be a dictionary")

        for name, conn in config["connections"].items():
            if not isinstance(conn, dict):
                raise ValueError(f"Connection '{name}' must be a dictionary")

            required_fields = ["hostname", "username"]
            for field in required_fields:
                if field not in conn:
                    raise ValueError(
                        f"Connection '{name}' is missing required field '{field}'"
                    )

            if "auth_method" not in conn:
                conn["auth_method"] = "key"  # Default to key-based auth

            if conn["auth_method"] not in ["key", "password"]:
                raise ValueError(
                    f"Connection '{name}' has invalid auth_method '{conn['auth_method']}'"
                )

            if conn["auth_method"] == "key" and "key_path" not in conn:
                # Default to ~/.ssh/id_rsa if not specified
                conn["key_path"] = os.path.expanduser("~/.ssh/id_rsa")

            if conn["auth_method"] == "password" and "password" not in conn:
                raise ValueError(
                    f"Connection '{name}' is missing required field 'password' for password authentication"
                )

            if "port" not in conn:
                conn["port"] = 22  # Default SSH port

    def get_connection_config(self, connection_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific connection.

        Args:
            connection_name: The name of the connection.

        Returns:
            Dict containing the connection configuration.

        Raises:
            ValueError: If the connection is not found.
        """
        if connection_name not in self.config["connections"]:
            raise ValueError(
                f"Connection '{connection_name}' not found in configuration"
            )

        return self.config["connections"][connection_name]

    def get_allowed_commands(self) -> List[str]:
        """
        Get the list of allowed commands.

        Returns:
            List of allowed command strings.
        """
        return self.config.get("defaults", {}).get("allowed_commands", [])

    def get_timeout(self) -> int:
        """
        Get the command timeout.

        Returns:
            Timeout in seconds.
        """
        return self.config.get("defaults", {}).get("timeout", 30)

    def get_max_output_size(self) -> int:
        """
        Get the maximum output size.

        Returns:
            Maximum output size in bytes.        """
        return self.config.get("defaults", {}).get(
            "max_output_size", 1048576
        )  # Default 1MB

    def get_connection_names(self) -> List[str]:
        """
        Get the list of connection names.

        Returns:
            List of connection name strings.
        """
        return list(self.config["connections"].keys())

    def reload_config(self) -> None:
        """
        Reload the configuration from the config file.
        
        This allows runtime updates to the configuration without restarting the server.
        """
        self.config = self._load_config()
