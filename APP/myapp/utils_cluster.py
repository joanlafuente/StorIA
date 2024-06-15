
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path
from argparse import ArgumentParser
import time

def receive_image(remote_image_path, local_path, hostname, port, username, password):
    # Initialize SSH client
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server with the specified port
    ssh.connect(hostname, port=port, username=username, password=password)

    # SCPClient takes a paramiko transport as an argument
    scp = SCPClient(ssh.get_transport())

    # Transfer the file
    scp.get(remote_image_path, local_path)

    # Close SCP Client
    scp.close()

    # Close the SSH connection
    ssh.close()

def send_image(local_image_path, remote_path, hostname, port, username, password):
    # Initialize SSH client
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server with the specified port
    ssh.connect(hostname, port=port, username=username, password=password)

    # SCPClient takes a paramiko transport as an argument
    scp = SCPClient(ssh.get_transport())

    # Transfer the file
    scp.put(local_image_path, remote_path)

    # Close SCP Client
    scp.close()

    # Close the SSH connection
    ssh.close()


def execute_ssh_command(host, port, username, password, command):
    # Initialize the SSH client
    client = paramiko.SSHClient()
    
    # Add the host key (this is not the safest approach, consider a better host key policy)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the server
        client.connect(hostname=host, port=port, username=username, password=password)
        
        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        
        # Read the standard output and print it
        print(stdout.read().decode())
        
        # Read the standard error and print it if not empty
        if stderr:
            print(stderr.read().decode())
    
    finally:
        # Close the connection
        client.close()
