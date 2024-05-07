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


import paramiko

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


# Folder from which we are going to send the images of the wacom output to the cluster
FOLDER_SENDING_FROM_LOCAL = Path('Outputs/Wacom/Png_final_results')

# Folder in which we are going to save the image of the text2Sketch model in the cluster
FOLDER_SAVING_TO_LOCAL = Path('Outputs/Sketch2image')

# Folder from which we are going to retrieve the images from the text2Sketch model
FOLDER_GETTING_FROM_CLUSTER = Path('/hhome/nlp2_g05/social_inovation/Generated_imgs')

HOSTNAME = '158.109.75.52'
PORT = '55022'
USERNAME = 'nlp2_g05'
PASWORD = 'nlp_07'

def args():
    parser = ArgumentParser()
    parser.add_argument("--source", type=Path, help="source image file")
    args = parser.parse_args()
    path = args.source
    filename = path.name.split(".")[0]
    print(path, filename)
    return path, filename

if __name__ == '__main__':
    # Receive the images from the text2Sketch model
    #path, filename = args()  # This is the filename that needs to match with the one in the cluster folder
    filename = "sketch.png"
    generated_img = 'image.png'
    
    send_image('/home/nbiescas/Desktop/Story-Generation-1/Sketches/sketch.png', 
           '/hhome/nlp2_g05/social_inovation/Sketches', 
           '158.109.75.52', 
           '55022',
           'nlp2_g05', 
           'nlp_07')
    time.sleep(1)
    
    execute_ssh_command(HOSTNAME, PORT, USERNAME, PASWORD, "bash /hhome/nlp2_g05/social_inovation/bash_script.sh")
    
    time.sleep(1)
    receive_image(remote_image_path = FOLDER_GETTING_FROM_CLUSTER / generated_img,
                  local_path        = FOLDER_SAVING_TO_LOCAL,
                  hostname          = HOSTNAME,
                  port              = PORT,
                  username          = USERNAME,
                  password          = PASWORD)
    

    #send_image(local_image_path = FOLDER_SENDING_FROM_LOCAL / filename + '.png',
    #           remote_path       = FOLDER_STORING_IN_CLUSTER,
    #           hostname          = HOSTNAME,
    #           port              = PORT,
    #           username          = USERNAME)

