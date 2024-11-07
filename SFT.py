import os
import sys
import json
import bcrypt
import logging
import paramiko
from datetime import datetime
from colorama import Fore, Style, init
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def print_prog_name():
	print(Fore.MAGENTA + """
███████╗██╗     ██████╗  █████╗ ████████╗██████╗ ██╗███╗   ██╗██╗   ██╗███╗   ███╗
██╔════╝██║     ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██║████╗  ██║██║   ██║████╗ ████║
█████╗  ██║     ██████╔╝███████║   ██║   ██████╔╝██║██╔██╗ ██║██║   ██║██╔████╔██║
██╔══╝  ██║     ██╔═══╝ ██╔══██║   ██║   ██╔══██╗██║██║╚██╗██║██║   ██║██║╚██╔╝██║
███████╗███████╗██║     ██║  ██║   ██║   ██║  ██║██║██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝
""")
	print(Fore.BLUE + """
			
                        ┏┓         ┏┓•┓    ┏┳┓       ┏      
                        ┗┓┏┓┏┏┓┏┓  ┣ ┓┃┏┓   ┃ ┏┓┏┓┏┓┏╋┏┓┏┓  
                        ┗┛┗┗┻┛ ┗   ┻ ┗┗┗    ┻ ┛ ┗┻┛┗┛┛┗ ┛   
                                    
""" + Style.RESET_ALL)

def encrypt_file(input_file, output_file, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        f_out.write(iv)
        data = f_in.read()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        f_out.write(encrypted_data)

def decrypt_file(input_file, output_file, key):
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        iv = f_in.read(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        data = f_in.read()
        unpadded_data = decryptor.update(data) + decryptor.finalize()
        f_out.write(unpadded_data)

def sftp_transfer_file(host, port, username, key_file, local_file, remote_file, upload=True):
    try:
        print(Fore.BLUE + "Connecting to " + Style.RESET_ALL + f"{host}:{port} as {username} with key {key_file}")
        transport = paramiko.Transport((host, port))
        private_key = paramiko.RSAKey(filename=key_file)
        transport.connect(username=username, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        if upload:
            sftp.put(local_file, remote_file)
            print(Fore.GREEN + "Uploaded " + Style.RESET_ALL + f"{local_file} to {remote_file}")
        else:
            sftp.get(remote_file, local_file)
            print(Fore.GREEN + "Downloaded " + Style.RESET_ALL + f"{remote_file} to {local_file}" + Style.RESET_ALL)

        sftp.close()
        transport.close()
        print(Fore.BLUE + "Connection closed" + Style.RESET_ALL)
        return True
    except paramiko.ssh_exception.AuthenticationException:
        print(Fore.RED + "Authentication failed. " + Style.RESET_ALL + "Please check your key and server settings.")
        return False
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
        return False


def create_user(username, role):
    password = input(f"Enter password for {username}: ")
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return {"username": username, "role": role, "password_hash": password_hash}

def save_users(users, filename="users.json"):
    with open(filename, 'w') as f:
        json.dump(users, f)

def load_users(filename="users.json"):
    with open(filename, 'r') as f:
        return json.load(f)

def authenticate_user(users, username, password):
    user_data = users.get(username)
    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data["password_hash"].encode('utf-8')):
        return True
    else:
        print(Fore.RED + "Authentication failed." + Style.RESET_ALL)
        sys.exit("Exiting program due to failed authentication.")

users = load_users()

logging.basicConfig(filename='audit_log.txt', level=logging.INFO)

def log_event(event):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{timestamp} - {event}")

def main():
    print_prog_name()

    key = os.urandom(32)
    
    username = input(Fore.YELLOW + "Enter username: " + Style.RESET_ALL)
    password = input(Fore.YELLOW + "Enter password: " + Style.RESET_ALL)
    if authenticate_user(users, username, password):
        print(Fore.GREEN + "Authentication successful."+ Style.RESET_ALL)
    remote_host = input(Fore.YELLOW + "Enter the remot host ip: " + Style.RESET_ALL)
    input_file = input(Fore.YELLOW + "Enter the name of the file: " + Style.RESET_ALL)
    encrypted_file = 'encrypted_' + input_file
    save_path = input(Fore.YELLOW + "Enter the path to save the file: " + Style.RESET_ALL)
    key_file = os.path.expanduser('~/.ssh/id_rsa')

    encrypt_file(input_file, encrypted_file, key)
    log_event(f"File {input_file} encrypted by {username}")

    if sftp_transfer_file(remote_host, 22, username, key_file, encrypted_file, save_path + "/" + encrypted_file, upload=True):
        log_event(f"File {encrypted_file} transferred to remote server by {username}")

    # Simulate file transfer back for decryption
    # decrypted_file = input(Fore.YELLOW + "Enter the name to save the decrypted file: " + Style.RESET_ALL)
    # sftp_transfer_file(remote_host, 22, username, key_file, encrypted_file, save_path + "/" + encrypted_file, upload=False)

    # # Ensure the decrypted file is saved in the specified path
    # decrypted_full_path = os.path.join(save_path, decrypted_file)
    # decrypt_file(encrypted_file, decrypted_full_path, key)
    # log_event(f"File {decrypted_full_path} decrypted by {username}")

    # Ensure encrypted file is deleted after decryption
    if os.path.exists(encrypted_file):
        os.remove(encrypted_file)
        log_event(f"File {encrypted_file} deleted")

if __name__ == "__main__":
    main()
