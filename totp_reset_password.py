#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import getpass
import pyotp
import syslog
import pwd

DEFAULT_SECRETS_DIR = "/etc/totp_secrets_encrypted"

# ---------------------------
# Helpers
# ---------------------------

def decrypt_secret(user, key_file, secrets_dir):
    path = os.path.join(secrets_dir, user + ".enc")
    if not os.path.exists(path):
        return None
    cmd = [
        "openssl", "enc", "-d", "-aes-256-cbc", "-in", path,
        "-pass", f"file:{key_file}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()

def verify_otp(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

def reset_password(user):
    try:
        subprocess.run(["passwd", user], check=True)
    except subprocess.CalledProcessError:
        print("Password reset failed.")
        sys.exit(1)

def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except KeyError:
        return False

# ---------------------------
# Main
# ---------------------------

def main():
    if os.geteuid() != 0:
        print("Must be run as root.")
        sys.exit(1)

    key_file = os.getenv("TOTP_MASTER_KEY")
    secrets_dir = os.getenv("TOTP_SECRETS_DIR") or DEFAULT_SECRETS_DIR
    if not key_file or not os.path.exists(key_file):
        print("Error: TOTP master key missing! Set TOTP_MASTER_KEY")
        sys.exit(1)
    if not os.path.exists(secrets_dir):
        print(f"Error: Secrets directory {secrets_dir} missing!")
        sys.exit(1)

    user = input("Enter username: ").strip()
    if not user_exists(user):
        print("User does not exist.")
        sys.exit(1)

    secret = decrypt_secret(user, key_file, secrets_dir)
    if not secret:
        print("Error: Could not read TOTP secret for user.")
        sys.exit(1)

    for _ in range(3):
        code = getpass.getpass("Enter TOTP code: ")
        if verify_otp(secret, code):
            print("TOTP verified! Resetting password...")
            reset_password(user)
            syslog.syslog(syslog.LOG_AUTH | syslog.LOG_NOTICE,
                          f"TOTP password reset for user {user}")
            print("Password reset successfully.")
            sys.exit(0)
        else:
            print("Incorrect TOTP code.")

    print("Maximum attempts exceeded. Aborting.")
    sys.exit(1)

if __name__ == "__main__":
    main()