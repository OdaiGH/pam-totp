#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import syslog
import pyotp
import pwd
import subprocess

DEFAULT_SECRETS_DIR = "/etc/totp_secrets_encrypted"

# ---------------------------
# Helpers
# ---------------------------

def decrypt_secret(user):
    key_file = os.getenv("TOTP_MASTER_KEY")
    secrets_dir = os.getenv("TOTP_SECRETS_DIR") or DEFAULT_SECRETS_DIR
    if not key_file or not os.path.exists(key_file):
        return None
    if not os.path.exists(secrets_dir):
        return None
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

def user_exists(user):
    try:
        pwd.getpwnam(user)
        return True
    except KeyError:
        return False

def is_admin(user):
    # Basic check: if UID is 0 (root) → skip OTP
    try:
        return pwd.getpwnam(user).pw_uid == 0
    except KeyError:
        return False

# -------------------------------
# PAM module functions
# -------------------------------

def pam_sm_authenticate(pamh, flags, argv):
    try:
        user = pamh.get_user()
    except pamh.exception as e:
        return e.pam_result

    if user is None or not user_exists(user):
        return pamh.PAM_AUTH_ERR

    # Skip OTP for root/admin
    if is_admin(user):
        syslog.syslog(syslog.LOG_AUTH | syslog.LOG_NOTICE,
                      f"Admin/root {user} bypassed TOTP")
        return pamh.PAM_SUCCESS

    secret = decrypt_secret(user)
    if not secret:
        return pamh.PAM_AUTH_ERR

    for _ in range(3):
        msg = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "Enter TOTP code: ")
        resp = pamh.conversation(msg)
        if verify_otp(secret, resp.resp):
            syslog.syslog(syslog.LOG_AUTH | syslog.LOG_NOTICE,
                          f"TOTP login success for user {user}")
            return pamh.PAM_SUCCESS

    syslog.syslog(syslog.LOG_AUTH | syslog.LOG_WARNING,
                  f"TOTP login failed for user {user}")
    return pamh.PAM_AUTH_ERR

def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS