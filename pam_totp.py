#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pwd
import syslog
import pyotp


def get_user_secret_key(user):
    try:
        return pwd.getpwnam(user).pw_gecos
    except KeyError:
        return -1


def verify_otp(secret, entered_otp):
    totp = pyotp.TOTP(secret)
    otp = totp.now()
    return otp == entered_otp


def pam_sm_authenticate(pamh, flags, argv):
    try:
        user = pamh.get_user()
        user_secret = get_user_secret_key(user)
    except pamh.exception, e:
        return e.pam_result
    if user == "root":
	return pamh.PAM_SUCCESS 
    if user is None or user_secret == -1:
        msg = pamh.Message(pamh.PAM_ERROR_MSG,
                           'Something went wrong. Contact your System Adminstrator'
                           )
        pamh.conversation(msg)
        return pamh.PAM_ABORT

    for attempt in range(0, 3):
        msg = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, 'Enter OTP: ')
        resp = pamh.conversation(msg)
        otp = verify_otp(user_secret, resp.resp)
        if otp:
            return pamh.PAM_SUCCESS
        continue
    msg = pamh.Message(pamh.PAM_ERROR_MSG,
                       'otp for user {} is incorrect'.format(user))
    pamh.conversation(msg)
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    return pamh.PAM_SUCCESS


def pam_sm_open_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS


def pam_sm_chauthtok(pamh, flags, argv):
    return pamh.PAM_SUCCESS
