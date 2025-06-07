"""
Mock SSH server for testing SSH-MCP.

This module provides a mock SSH server for testing SSH connections without a real SSH server.
"""

import os
import socket
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import paramiko


class MockSSHServer:
    """
    A mock SSH server for testing SSH-MCP without a real SSH server.

    This server implements a basic SSH server that accepts connections
    and responds to commands with predefined outputs.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,  # 0 means pick an available port
        username: str = "testuser",
        password: Optional[str] = "testpass",
        key_path: Optional[str] = None,
    ):
        """
        Initialize the mock SSH server.

        Args:
            host: The host address to bind to.
            port: The port to bind to. If 0, an available port will be chosen.
            username: The username to accept for authentication.
            password: The password to accept for authentication.
            key_path: Path to a private key to use for server host key.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path

        # Generate a server key if not provided
        if key_path and os.path.exists(key_path):
            self.server_key = paramiko.RSAKey(filename=key_path)
        else:
            self.server_key = paramiko.RSAKey.generate(2048)

        # Command handlers
        self.command_handlers: Dict[str, Callable] = {
            "ls": self._handle_ls,
            "cat": self._handle_cat,
            "echo": self._handle_echo,
            "pwd": self._handle_pwd,
            "whoami": self._handle_whoami,
        }

        # Server state
        self.server_socket = None
        self.server_thread = None
        self.running = False

    def start(self) -> None:
        """
        Start the mock SSH server.

        This method starts the server in a separate thread.
        """
        if self.running:
            return

        try:
            # Create a socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            # Get the actual port if we used 0
            self.port = self.server_socket.getsockname()[1]

            # Start the server thread
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"Mock SSH server started on {self.host}:{self.port}")

        except Exception as e:
            print(f"Failed to start mock SSH server: {str(e)}")
            if self.server_socket:
                self.server_socket.close()
            self.running = False

    def stop(self) -> None:
        """
        Stop the mock SSH server.
        """
        self.running = False
        if self.server_socket:
            self.server_socket.close()

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1.0)

        print("Mock SSH server stopped")

    def _run_server(self) -> None:
        """
        Run the server loop.

        This method runs in a separate thread and accepts connections.
        """
        try:
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Connection from {client_address[0]}:{client_address[1]}")

                    # Handle the connection in a new thread
                    client_thread = threading.Thread(
                        target=self._handle_client, args=(client_socket,)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except (socket.error, OSError):
                    if not self.running:
                        break
                    raise

        except Exception as e:
            if self.running:
                print(f"Server error: {str(e)}")

        finally:
            if self.server_socket:
                self.server_socket.close()

    def _handle_client(self, client_socket: socket.socket) -> None:
        """
        Handle a client connection.

        Args:
            client_socket: The client socket.
        """
        transport = None

        try:
            # Set up the transport
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self.server_key)

            # Set up the server interface
            server_handler = MockSSHServerHandler(self.username, self.password)
            server_handler.command_handlers = self.command_handlers

            # Start the server
            transport.start_server(server=server_handler)

            # Wait for channels and handle them
            while transport.is_active():
                channel = transport.accept(1)
                if channel is None:
                    continue

                # Handle the channel in the server handler
                server_handler.handle_session(channel)
                break

        except Exception as e:
            print(f"Error handling client: {str(e)}")

        finally:
            if transport:
                transport.close()

    # Command handlers
    def _handle_ls(self, args: List[str]) -> Tuple[int, str, str]:
        """Handle ls command."""
        if "-la" in args:
            output = (
                "total 20\n"
                "drwxr-xr-x 2 user user 4096 Jun  7 12:34 .\n"
                "drwxr-xr-x 6 user user 4096 Jun  7 12:30 ..\n"
                "-rw-r--r-- 1 user user  123 Jun  7 12:32 file1.txt\n"
                "-rw-r--r-- 1 user user  456 Jun  7 12:33 file2.txt\n"
            )
        else:
            output = "file1.txt\nfile2.txt\n"

        return 0, output, ""

    def _handle_cat(self, args: List[str]) -> Tuple[int, str, str]:
        """Handle cat command."""
        if not args:
            return 1, "", "cat: missing operand"

        filename = args[0]

        if filename == "file1.txt":
            return 0, "This is the content of file1.txt\n", ""
        elif filename == "file2.txt":
            return 0, "This is the content of file2.txt\nIt has multiple lines.\n", ""
        else:
            return 1, "", f"cat: {filename}: No such file or directory"

    def _handle_echo(self, args: List[str]) -> Tuple[int, str, str]:
        """Handle echo command."""
        return 0, " ".join(args) + "\n", ""

    def _handle_pwd(self, args: List[str]) -> Tuple[int, str, str]:
        """Handle pwd command."""
        return 0, "/home/testuser\n", ""

    def _handle_whoami(self, args: List[str]) -> Tuple[int, str, str]:
        """Handle whoami command."""
        return 0, f"{self.username}\n", ""


class MockSSHServerHandler(paramiko.ServerInterface):
    """
    SSH server interface handler for the mock SSH server.
    """

    def __init__(self, username: str, password: Optional[str] = None):
        """
        Initialize the server handler.

        Args:
            username: The username to accept.
            password: The password to accept.
        """
        self.username = username
        self.password = password
        self.command_handlers = {}
        self.channel = None

    def check_channel_request(self, kind: str, chanid: int) -> int:
        """
        Check if a channel request is acceptable.

        Args:
            kind: The kind of channel requested.
            chanid: The channel ID.

        Returns:
            OPEN_SUCCEEDED if the request is acceptable, or an error code.
        """
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        """
        Check password authentication.

        Args:
            username: The username.
            password: The password.

        Returns:
            AUTH_SUCCESSFUL if the authentication is successful, or an error code.
        """
        if username == self.username and password == self.password:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        """
        Check public key authentication.

        Args:
            username: The username.
            key: The public key.

        Returns:
            AUTH_SUCCESSFUL if the authentication is successful, or an error code.
        """
        # For simplicity, we'll accept any key for the correct username
        if username == self.username:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username: str) -> str:
        """
        Get the allowed authentication methods.

        Args:
            username: The username.

        Returns:
            String containing the allowed authentication methods.
        """
        if self.password:
            return "password,publickey"
        return "publickey"

    def check_channel_shell_request(self, channel: paramiko.Channel) -> bool:
        """
        Check if a shell request is acceptable.

        Args:
            channel: The channel.

        Returns:
            True if the request is acceptable, False otherwise.
        """
        # Accept a shell request
        return True

    def check_channel_exec_request(
        self, channel: paramiko.Channel, command: bytes
    ) -> bool:
        """
        Check if an exec request is acceptable.

        Args:
            channel: The channel.
            command: The command to execute.

        Returns:
            True if the request is acceptable, False otherwise.
        """
        # Accept the exec request and handle the command in a separate thread
        # to avoid blocking
        threading.Thread(
            target=self._handle_command,
            args=(channel, command.decode("utf-8")),
            daemon=True,
        ).start()
        return True

    def handle_session(self, channel: paramiko.Channel) -> None:
        """
        Handle a session.

        Args:
            channel: The channel.
        """
        # Wait for the command to complete or channel to close
        try:
            while channel.active and not channel.closed:
                time.sleep(0.1)
        except Exception:
            pass
        finally:
            if channel.active and not channel.closed:
                channel.close()

    def _handle_command(self, channel: paramiko.Channel, command: str) -> None:
        """
        Handle a command.

        Args:
            channel: The channel.
            command: The command to execute.
        """
        try:
            # Parse the command
            parts = command.strip().split()
            if not parts:
                exit_code = 1
                stdout = ""
                stderr = "Empty command"
            else:
                base_command = parts[0]
                args = parts[1:]

                # Check if we have a handler for this command
                if base_command in self.command_handlers:
                    exit_code, stdout, stderr = self.command_handlers[base_command](
                        args
                    )
                else:
                    exit_code = 127
                    stdout = ""
                    stderr = f"Command not found: {base_command}"

            # Send the output
            if stdout:
                channel.send(stdout.encode("utf-8"))
            if stderr:
                channel.send_stderr(stderr.encode("utf-8"))

            # Set the exit code and close
            channel.send_exit_status(exit_code)
            channel.close()

        except Exception as e:
            # Handle any errors
            try:
                channel.send_stderr(
                    f"Error executing command: {str(e)}\n".encode("utf-8")
                )
                channel.send_exit_status(1)
                channel.close()
            except Exception:
                pass


def main():
    """Run a mock SSH server for testing."""
    server = MockSSHServer(port=2222)
    server.start()

    try:
        print("Mock SSH server running. Press Ctrl+C to stop.")
        while True:
            import time

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping server...")

    finally:
        server.stop()


if __name__ == "__main__":
    main()
