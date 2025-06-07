# SSH-MCP Project Plan

This document outlines the plan for creating an MCP server that enables Large Language Models (LLMs) to execute commands on remote servers via SSH.

## Project Goal

Create an MCP server that allows LLMs to:
1. Securely connect to remote servers using SSH
2. Execute commands on those servers
3. Retrieve results back to the LLM
4. Configure connections via a YAML file in the user's home directory

## Architecture

### High-Level Components

1. **MCP Server**: The central component that exposes resources and tools to LLMs following the Model Context Protocol
2. **SSH Connection Manager**: Handles establishing and managing SSH connections to remote servers
3. **Configuration Manager**: Loads and validates user configuration from ~/.ssh-mcp-config.yaml
4. **Command Executor**: Executes commands on remote servers and processes the results
5. **Result Parser**: Formats command outputs for proper presentation to the LLM

### Component Relationships

```
+----------------+      +---------------------+      +------------------+
|                |      |                     |      |                  |
|   MCP Server   |----->| SSH Connection Mgr  |----->| Remote SSH Server|
|                |      |                     |      |                  |
+-------+--------+      +----------+----------+      +------------------+
        |                          |
        |                          |
        v                          v
+----------------+      +---------------------+
|                |      |                     |
| Result Parser  |<-----| Command Executor    |
|                |      |                     |
+----------------+      +---------------------+
        ^
        |
        |
+-------+--------+
|                |
| Config Manager |
|                |
+----------------+
```

## Tasks Breakdown

### 1. Project Setup
- [x] Initialize the Python project using uv
- [x] Add required dependencies (mcp, paramiko, pyyaml)
- [x] Create basic project structure

### 2. Configuration Management
- [x] Design the YAML configuration schema
- [x] Implement a configuration loader that reads from ~/.ssh-mcp-config.yaml
- [x] Add validation for the configuration
- [x] Create default configuration if not present

### 3. SSH Connection Management
- [x] Implement SSH connection class using Paramiko
- [x] Support various authentication methods (password, key-based)
- [x] Handle connection timeouts and errors
- [x] Implement connection pooling for efficiency

### 4. Command Execution
- [x] Implement command execution on remote servers
- [x] Capture stdout, stderr, and exit codes
- [x] Implement timeout handling for commands
- [x] Support for interactive commands (if feasible)

### 5. MCP Server Implementation
- [x] Create the FastMCP server setup
- [x] Define resources for connection information
- [x] Implement tools for command execution
- [x] Design the response format for command results

### 6. Testing
- [x] Create unit tests for individual components
- [x] Set up integration tests with a mock SSH server
- [x] Test with various LLM interfaces

### 7. Documentation
- [x] Write documentation for setting up the server
- [x] Document the configuration file format
- [x] Document security considerations

## Configuration File Example

```yaml
# ~/.ssh-mcp-config.yaml
connections:
  server1:
    hostname: example.com
    port: 22
    username: user
    auth_method: key  # or password
    key_path: ~/.ssh/id_rsa  # only needed for key auth
    password: null  # only needed for password auth
    
  server2:
    hostname: another-server.com
    port: 2222
    username: admin
    auth_method: password
    password: ${SSH_PASSWORD}  # Use environment variable

defaults:
  timeout: 30  # seconds
  max_output_size: 1048576  # 1MB
```

## Security Considerations

1. **Authentication Security**: Store sensitive information securely
2. **Command Validation**: Implement command allowlisting to prevent arbitrary command execution
3. **Output Limitations**: Set limits on output size to prevent excessive resource usage
4. **Connection Pooling**: Properly manage and limit connections
5. **Logging**: Implement proper logging for security auditing
