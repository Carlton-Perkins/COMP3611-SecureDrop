#!/usr/bin/env python3

# import os
import cmd, pathlib, configparser, getpass, crypt
from hmac import compare_digest as comp_hash

CONFIGFILE = pathlib.Path('~/.secure_drop/config').expanduser()

def main():
    print('Something')
    if (not isRegistered()):
        register()
        cleanUpAndExit()

    # login()

    Shell().cmdloop()
    

class Shell(cmd.Cmd):
    intro = ''
    prompt = 'Secure_Drop> '

    def do_exit(self, args):
        'Exit the program'
        cleanUpAndExit()
    def do_add(self, args):
        'Add a new contact'
        print('Add')
    def do_list(self, args):
        'List all online contacts'
        print('list')
    def do_send(self, args):
        'Transfer a file to contact'
        print('send')

def isRegistered():
    config = getConfig()

    try:
        config['Cred']['name']
        config['Cred']['email']
        config['Cred']['password']

        return True
    except KeyError:
        return False
    
def register():
    print('Register')

    name = input('Enter your full name: ')
    email = input('Enter your email address: ')
    password = cryptPassword(getpass.getpass('Enter your password: '))
    if (not checkPassword(getpass.getpass('Re-enter your password: '), password)):
        exit('Password Mismatch, Registration cancelled')

    print('Registration Successful')

    config = getConfig()

    config['Cred'] = {
        'name':name,
        'email':email,
        'password':password}

    writeConfig(config)

def checkPassword(plaintext, crypt):
    return comp_hash(cryptPasswordSalted(plaintext, crypt), crypt)

def cryptPassword(plaintext):
    # Crypt will always use strongest salt available
    return crypt.crypt(plaintext)
def cryptPasswordSalted(plaintext, salt):
    return crypt.crypt(plaintext, salt)

def getConfig():
    config = configparser.ConfigParser()
    if (CONFIGFILE.exists()):
        with open(CONFIGFILE, "r") as fp:
            config.read_file(fp)
    return config

def writeConfig(config):
    with open(CONFIGFILE, "w+") as fp:
        config.write(fp)
    
def cleanUpAndExit():
    print('Exit SecureDrop')
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Force closing the application due to SIG')
