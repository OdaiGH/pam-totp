# pam-totp

PAM TOTP is a Linux Pluggable Authentication Module (PAM) that enables 2fa using a Time-based OTP method

# Installation

* you need to install `pam-python` . Check this repo https://github.com/stackhpc/pam-python

* clone this project and add the following line

`auth       requisite     pam_python.so /PATH/TO/THE/CODE/pam_totp.py`

to the end of file  `/etc/pam.d/common-auth`

# Setup
each user  must have his own secret key use and we will do this by using this command:

`usermod user -c "abcdabcd"`

now when you switch to user by using

`su user`

it will ask for both your password and your otp


![image](https://user-images.githubusercontent.com/2572236/186054741-bfc2a1ce-10af-4556-8309-2e5d710f3357.png)


even ssh reqiures you to enter your otp

![image](https://user-images.githubusercontent.com/2572236/186056218-54c73611-f07b-4e92-b7b0-8ec20b025311.png)



use this website to verify your otp  https://totp.app/

you could also use google authenticator, you just need to add your key
