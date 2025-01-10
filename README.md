# Secure File Encryption and Transfer

This Python project implements a secure file encryption, decryption, and transfer system that uses AES encryption, SFTP for file transfer, and bcrypt for user authentication. It allows a user to securely encrypt files, transfer them to a remote server, and decrypt them using the AES encryption algorithm. The system also includes logging and audit features for tracking user actions.

## Features

- **AES File Encryption & Decryption**: Encrypt and decrypt files using AES encryption in CBC mode with a key from a `key.bin` file.
- **SFTP File Transfer**: Upload and download files to/from a remote server via SFTP using RSA private key authentication.
- **User Authentication**: Authenticate users via username and password, with password hashes stored securely using bcrypt.
- **Audit Logging**: All important actions, including file encryption, decryption, transfer, and deletion, are logged with timestamps for auditing purposes.
- **Interactive Command-Line Interface**: Provides an interactive CLI for users to choose from different actions like file encryption, decryption, or transfer.

## Requirements

- Python 3.x
- Dependencies:
  - `paramiko` for SFTP functionality
  - `bcrypt` for password hashing and authentication
  - `cryptography` for AES encryption/decryption
  - `colorama` for colored CLI output
  - `logging` for audit logging
  - `getpass` for secure password input

To install the required libraries, run:

```bash
pip install paramiko bcrypt cryptography colorama
```

## Setup

1. **Create or Modify User Database**: 
    - Users and their roles are stored in a JSON file (`users.json`), and passwords are hashed using bcrypt.
    - The `create_user` function can be used to create new users, and `save_users` saves the list of users to the JSON file.
    
2. **Key File**:
    - Ensure you have a private key (`id_rsa`) available at `~/.ssh/id_rsa` or specify a custom path in the script.
    - The AES key should be stored in a binary file (`key.bin`), which is used for encrypting and decrypting files.

3. **Log File**:
    - Actions are logged to `audit_log.txt`. Ensure you have write access to this file.

## Usage

Once the script is configured and the required dependencies are installed, you can run the program using:

```bash
python secure_file_transfer.py
```

### Options:
Upon successful authentication, users can choose from the following actions:
- **Send (1)**: Encrypt a file and transfer it to a remote server via SFTP.
- **Encrypt (2)**: Encrypt a local file.
- **Decrypt (3)**: Decrypt an encrypted file.

### Authentication:
- The user is prompted for a username and password.
- The password is checked against stored hashed passwords using bcrypt for authentication.

### Encryption and Decryption:
- Files are encrypted using AES with CBC mode, and the encryption key is read from the `key.bin` file.
- The initialization vector (IV) is randomly generated and prepended to the encrypted file.
- Files can be decrypted by using the appropriate AES key and IV from the encrypted file.

### File Transfer:
- Files can be uploaded or downloaded from a remote server via SFTP. The private key for authentication is used in the transfer.

### Logging:
- Every action, such as file encryption, decryption, transfer, and deletion, is logged to `audit_log.txt` with a timestamp and description.

## Example

1. **Encrypt and Transfer a File**:
   - User selects option `1` (Send).
   - The script prompts for the remote server's IP address, local file path, and the path to save the encrypted file on the remote server.
   - The file is encrypted and then transferred to the remote server via SFTP.

2. **Decrypt a File**:
   - User selects option `3` (Decrypt).
   - The script prompts for the encrypted file name and the output file name to save the decrypted file.

3. **Log File**:
   - All events, such as file encryption and transfer, are logged with the following format:
   
     ```
     2025-01-10 15:23:45 - File example.txt encrypted by username
     2025-01-10 15:24:00 - File example.txt transferred to remote server by username
     ```

## Security Considerations

- **Password Security**: User passwords are never stored in plain text. They are hashed using bcrypt before being stored in the `users.json` file.
- **File Encryption**: AES (Advanced Encryption Standard) is used for file encryption, with a random IV for each encryption operation. This ensures data confidentiality.
- **Secure File Transfer**: SFTP is used to securely transfer files, and RSA private key authentication is employed to ensure secure connections.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributions

Feel free to fork the repository, submit issues, or open pull requests for any improvements.
