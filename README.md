# SSH-MCP

MCP server that enables LLMs to execute commands on remote servers via SSH.

## Overview

This project provides a Model Context Protocol (MCP) server that allows Large Language Models to:
- Connect to remote SSH servers
- Execute commands on those servers
- Retrieve the results

## Configuration

Create a configuration file at `~/.ssh-mcp-config.yaml` with your SSH connection details:

```yaml
connections:
  server1:
    hostname: example.com
    port: 22
    username: user
    auth_method: key  # or password
    key_path: ~/.ssh/id_rsa  # only needed for key auth
    
  server2:
    hostname: another-server.com
    port: 2222
    username: admin
    auth_method: password
    password: ${SSH_PASSWORD}  # Use environment variable

defaults:
  timeout: 30  # seconds
  max_output_size: 1048576  # 1MB
  allowed_commands:
    - ls
    - cat
    - grep
    # Add more allowed commands as needed
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ssh-mcp.git
cd ssh-mcp

# Install dependencies with uv
uv add "mcp[cli]" paramiko pyyaml

# Install the package
uv add --editable .
```

## Usage

Run the MCP server:

```bash
mcp dev ssh_mcp/server.py
```

## Security Considerations

- SSH-MCP implements command allowlisting to prevent arbitrary command execution
- Sensitive information like passwords should be provided via environment variables
- The configuration file should have appropriate permissions (chmod 600)
