import paramiko
import os

class SSHClient:
    """
    A class to interact with a VM over SSH.

    Attributes:
        hostname (str): The hostname of the VM.
        username (str): The username for SSH authentication.
        password (str): The password for SSH authentication.
        port (int): The port number for SSH connection. Defaults to 22.
        key_file (str): The path to the SSH key file for authentication.
    """

    def __init__(self, hostname, username, password=None, port=22, key_file=None):
        """
        Initialize the SSHClient.

        Args:
            hostname (str): The hostname of the VM.
            username (str): The username for SSH authentication.
            password (str): The password for SSH authentication. Defaults to None.
            port (int): The port number for SSH connection. Defaults to 22.
            key_file (str): The path to the SSH key file for authentication. Defaults to None.
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.key_file = key_file
        self.client = None

    def connect(self):
        """
        Establish an SSH connection to the VM.
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.key_file and os.path.exists(self.key_file):
            key = paramiko.RSAKey.from_private_key_file(self.key_file)
            self.client.connect(self.hostname, port=self.port, username=self.username, pkey=key)
        else:
            self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)

    def disconnect(self):
        """
        Close the SSH connection to the VM.
        """
        if self.client:
            self.client.close()

    def execute_command(self, command, dry_run=False):
        """
        Execute a command on the VM.

        Args:
            command (str): The command to execute.
            dry_run (bool): If True, perform a dry run (simulate command execution). Defaults to False.

        Returns:
            tuple: A tuple containing the stdout, stderr, and exit status.
        """
        if dry_run:
            print(f"Dry run: {command}")
            return "", "", 0
        else:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            return stdout.read().decode(), stderr.read().decode(), exit_status