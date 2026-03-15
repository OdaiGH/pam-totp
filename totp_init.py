#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import pyotp
import subprocess
import pwd

DEFAULT_SECRETS_DIR = "/etc/totp_secrets_encrypted"

# ---------------------------
# Helpers
# ---------------------------

def ensure_secrets_dir(secrets_dir):
    if not os.path.exists(secrets_dir):
        os.makedirs(secrets_dir, mode=0o700)
        print(f"Created encrypted secrets dir: {secrets_dir}")

def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except KeyError:
        return False

def generate_totp_secret():
    return pyotp.random_base32()

def encrypt_secret(secret, user, key_file, secrets_dir):
    path = os.path.join(secrets_dir, user + ".enc")
    cmd = [
        "openssl", "enc", "-aes-256-cbc", "-salt",
        "-in", "/dev/stdin", "-out", path, "-pass", f"file:{key_file}"
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    proc.communicate(input=secret.encode())
    if proc.returncode != 0:
        print("Error encrypting secret with OpenSSL")
        sys.exit(1)
    os.chmod(path, 0o600)
    print(f"Encrypted TOTP secret stored at {path}")

# ---------------------------
# Main
# ---------------------------

def main():
    if os.geteuid() != 0:
        print("Must be run as root.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Initialize TOTP for a user")
    parser.add_argument("-U", "--username", required=True, help="Username to create TOTP for")
    parser.add_argument("-s", "--secret", help="OpenSSL master key path (or TOTP_MASTER_KEY)")
    parser.add_argument("-d", "--dir", help="Secrets directory (or TOTP_SECRETS_DIR)")
    args = parser.parse_args()

    key_file = args.secret or os.getenv("TOTP_MASTER_KEY")
    if not key_file or not os.path.exists(key_file):
        print("Error: TOTP master key file missing! Set TOTP_MASTER_KEY or use -s")
        sys.exit(1)

    secrets_dir = args.dir or os.getenv("TOTP_SECRETS_DIR") or DEFAULT_SECRETS_DIR
    ensure_secrets_dir(secrets_dir)

    user = args.username
    if not user_exists(user):
        print(f"Error: User '{user}' does not exist")
        sys.exit(1)

    secret = generate_totp_secret()
    encrypt_secret(secret, user, key_file, secrets_dir)
    print(f"TOTP secret for {user} created successfully.")
    print(f"Secret (for reference if needed): {secret}")

if __name__ == "__main__":
    main()