# Paramiko API Summary

## Core SSH Protocol Classes

*   **Transport:** The foundation of SSH connections; manages encryption, authentication, and channels. ([docs](https://docs.paramiko.org/en/stable/api/transport.html))
    - **Key Methods:** `connect()`, `start_client()/start_server()`, `auth_*()`, `open_channel()`, `request_port_forward()`
    - **Usage:** `transport = paramiko.Transport(('hostname', 22)); transport.connect(username='user', password='pass')`

*   **Channel:** Socket-like communication tunnel over an SSH transport. ([docs](https://docs.paramiko.org/en/stable/api/channel.html))
    - **Key Methods:** `recv()/send()`, `exec_command()`, `invoke_shell()`, `get_pty()`, `recv_exit_status()`
    - **Usage:** `channel = transport.open_session(); channel.exec_command('ls')`

*   **Client (SSHClient):** High-level wrapper for SSH operations; manages host keys and authentication. ([docs](https://docs.paramiko.org/en/stable/api/client.html))
    - **Key Methods:** `connect()`, `exec_command()`, `invoke_shell()`, `open_sftp()`, `load_system_host_keys()`
    - **Usage:** `client = SSHClient(); client.connect('hostname', username='user', password='pass')`

*   **Message:** Handles SSH2 message encoding/decoding for protocol communication. ([docs](https://docs.paramiko.org/en/stable/api/message.html))
    - **Key Methods:** `add_string()/get_string()`, `add_int()/get_int()`, `asbytes()`
    - **Usage:** Internal component, rarely used directly

*   **Packetizer:** Manages SSH packet protocol, encryption, and framing. ([docs](https://docs.paramiko.org/en/stable/api/packet.html))
    - **Key Methods:** `read_message()`, `send_message()`, `set_*_cipher()`, `need_rekey()`
    - **Usage:** Internal component, accessed through Transport

## Authentication & Keys

*   **Authentication modules:** Handles various authentication methods. ([docs](https://docs.paramiko.org/en/stable/api/auth.html))
*   **SSH agents:** Interacts with SSH agents. ([docs](https://docs.paramiko.org/en/stable/api/agent.html))
*   **Host keys / known_hosts files:** Manages host keys and known_hosts files. ([docs](https://docs.paramiko.org/en/stable/api/hostkeys.html))
*   **Key handling:** Base classes and specific implementations for various key types (DSA, RSA, ECDSA, Ed25519). ([docs](https://docs.paramiko.org/en/stable/api/keys.html))
*   **GSS-API authentication:** Support for GSS-API based authentication. ([docs](https://docs.paramiko.org/en/stable/api/ssh_gss.html))
*   **GSS-API key exchange:** Support for GSS-API based key exchange. ([docs](https://docs.paramiko.org/en/stable/api/kex_gss.html))

## Other Primary Functions

*   **Configuration:** Manages SSH configuration options. ([docs](https://docs.paramiko.org/en/stable/api/config.html))
*   **ProxyCommand support:** Implements ProxyCommand functionality. ([docs](https://docs.paramiko.org/en/stable/api/proxy.html))
*   **Server implementation:** Provides tools for building SSH servers. ([docs](https://docs.paramiko.org/en/stable/api/server.html))
*   **SFTP:** Implements the SFTP protocol. ([docs](https://docs.paramiko.org/en/stable/api/sftp.html))

## Miscellany

*   **Buffered pipes:** Provides buffered pipe-like objects. ([docs](https://docs.paramiko.org/en/stable/api/buffered_pipe.html))
*   **Buffered files:** Provides buffered file-like objects. ([docs](https://docs.paramiko.org/en/stable/api/file.html))
*   **Cross-platform pipe implementations:** Platform-agnostic pipe implementations. ([docs](https://docs.paramiko.org/en/stable/api/pipe.html))
*   **Exceptions:** Defines custom exceptions used by Paramiko. ([docs](https://docs.paramiko.org/en/stable/api/ssh_exception.html))

## Key Usage Flow

1.  **Client:** Create an `SSHClient` object.
2.  **Server (Direct Control):** Pass a socket to a `Transport` object and use `start_server` or `start_client`.
3.  **Authentication (Client):** Authenticate using password or private key, check server's host key.
4.  **Authentication (Server):** Decide which users, passwords, and keys to allow.
5.  **Channels:** Either side can request flow-controlled `Channel` objects for communication.
