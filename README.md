# totp-pam-secure

A Python-based TOTP (Time-Based One-Time Password) authentication system for Linux. This module enhances system security by requiring a 2FA TOTP code during the PAM authentication process.

## Features

* **Encrypted Secrets:** OpenSSL AES-256 encrypted secrets for safe storage.
* **PAM Integration:** Seamless PAM module integration for login authentication (e.g., SSH).
* **CLI Tools:** Built-in utilities for initializing TOTP for users and resetting passwords.
* **Flexible Configuration:** Configurable via environment variables or CLI options.
* **Secure Access:** Root-only access for security, with root/admin bypass capabilities.

---

## Installation & Setup

### 1. Install Dependencies
Update your package list and install the required system packages and Python libraries:
```bash
sudo apt update
sudo apt install python3 python3-pip openssl -y
pip3 install pyotp
```

### 2. Generate the Master Key
Create a secure master key using OpenSSL and strict file permissions to ensure only root can read it:
```bash
sudo openssl rand -base64 32 > /etc/totp_master.key
sudo chmod 600 /etc/totp_master.key
export TOTP_MASTER_KEY=/etc/totp_master.key
```

### 3. Create the Secrets Directory
Set up the directory where the encrypted user TOTP secrets will be stored:
```bash
sudo mkdir /etc/totp_secrets_encrypted
sudo chmod 700 /etc/totp_secrets_encrypted
export TOTP_SECRETS_DIR=/etc/totp_secrets_encrypted
```

---

## Usage

### 1. Initialize TOTP for a User
Generate a new TOTP key for a specific user (replace `username` with the actual user):
```bash
sudo python3 totp_init.py -U username
```
> **Note:** Copy the secret key provided by the script's output and paste it into an authenticator app like Google Authenticator, Authy, or Bitwarden.

### 2. Reset a User's Password / TOTP
If a user loses their device or needs their 2FA reset (e.g., for the user `odai`), run:
```bash
sudo python3 totp_reset_password.py -U odai
```

---

## PAM Integration

To enforce TOTP during system authentication (like SSH), you must register the script as a PAM module.

### 1. Prepare the PAM Module
Ensure your Python PAM script is executable and located in the standard security directory:
```bash
sudo chmod 755 /usr/lib/security/pam_totp.py
```

### 2. Edit PAM Configuration
Open your target PAM configuration file (e.g., `/etc/pam.d/sshd` for SSH connections) and add the following line:
```text
auth required pam_exec.so expose_authtok /usr/lib/security/pam_totp.py
```

> **⚠️ Warning:** Always keep a secondary active root shell open while editing PAM configurations. If there is a syntax error or a bug in the script, you could lock yourself out of the system.
