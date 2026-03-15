# totp-pam-secure

A Python-based TOTP (Time-Based One-Time Password) authentication system for Linux with:

- OpenSSL AES-256 encrypted secrets
- PAM module integration for login authentication
- CLI tools for initializing TOTP for users and resetting passwords
- Flexible configuration via environment variables or CLI options
- Root-only access for security, with root/admin bypass

---

## installation

### 1. install deps
sudo apt update
sudo apt install python3 python3-pip openssl -y
pip3 install pyotp

### 2. generate master key 
sudo openssl rand -base64 32 > /etc/totp_master.key
sudo chmod 600 /etc/totp_master.key
export TOTP_MASTER_KEY=/etc/totp_master.key

### 3. create secret dir 
sudo mkdir /etc/totp_secrets_encrypted
sudo chmod 700 /etc/totp_secrets_encrypted
export TOTP_SECRETS_DIR=/etc/totp_secrets_encrypted

## Usage 

### 1. create key for a user
sudo python3 totp_init.py -U username

copy and paste into one of the autheticator apps like google-authenticator

### 2. resetting
sudo python3 totp_reset_password.py -U odai

### 3. add to pam
#### Edit PAM configuration file (e.g., /etc/pam.d/sshd) and add:
auth required pam_exec.so expose_authtok /usr/lib/security/pam_totp.py

#### sudo chmod 755 /usr/lib/security/pam_totp.py


