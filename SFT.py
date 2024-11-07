import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import paramiko
import logging
from datetime import datetime
from colorama import Fore, Style, init


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
    except paramiko.ssh_exception.AuthenticationException:
        print(Fore.RED + "Authentication failed. " + Style.RESET_ALL + "Please check your key and server settings.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

users = {
    "admin": User("admin", "admin"),
    "user": User("user", "user"),
    "elpatrinum": User("elpatrinum", "user")
}

def authenticate_user(username, password):
    return username in users and username == password

def authorize_user(username, resource):
    user = users.get(username)
    if user and user.role == "admin":
        return True
    return resource == "public_resource"

logging.basicConfig(filename='audit_log.txt', level=logging.INFO)

def log_event(event):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{timestamp} - {event}")

def main():
    print_prog_name()

    key = os.urandom(32)  # 32 bytes key for AES-256

    username = input(Fore.YELLOW + "Enter the Username: " + Style.RESET_ALL)

    remote_host = input(Fore.YELLOW + "Enter the remot host ip: " + Style.RESET_ALL)
    input_file = input(Fore.YELLOW + "Enter the name of the file: " + Style.RESET_ALL)
    encrypted_file = 'encrypted_' + input_file
    save_path = input(Fore.YELLOW + "Enter the path to save the file: " + Style.RESET_ALL)
    key_file = os.path.expanduser('~/.ssh/id_rsa')  # Ensure this path is correct

    if authenticate_user(username, username):
        if authorize_user(username, 'public_resource'):
            encrypt_file(input_file, encrypted_file, key)
            log_event(f"File {input_file} encrypted by {username}")

            # Transfer file to remote server
            sftp_transfer_file(remote_host, 22, username, key_file, encrypted_file, save_path + "/" + encrypted_file, upload=True)
            log_event(f"File {encrypted_file} transferred to remote server by {username}")

            # Simulate file transfer back for decryption
            # decrypted_file = input(Fore.YELLOW + "Enter the name to save the decrypted file: " + Style.RESET_ALL)
            # sftp_transfer_file(remote_host, 22, username, key_file, encrypted_file, f'/home/{username}/{encrypted_file}', upload=False)

            # # Ensure the decrypted file is saved in the specified path
            # decrypted_full_path = os.path.join(save_path, decrypted_file)
            # decrypt_file(encrypted_file, decrypted_full_path, key)
            # log_event(f"File {decrypted_full_path} decrypted by {username}")

            # Ensure encrypted file is deleted after decryption
            if os.path.exists(encrypted_file):
                os.remove(encrypted_file)
                log_event(f"File {encrypted_file} deleted after decryption")
        else:
            print(Fore.RED + "Authorization failed." + Style.RESET_ALL)
    else:
        print(Fore.RED + Fore.YELLOW +"Authentication failed." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
