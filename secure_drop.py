#!/usr/bin/env python3

# import os
import cmd # Supplies the subshell CMD prompt
import pathlib # Sane Path accessors/Validators
import configparser # .ini-ish file config accessor/generators
import getpass # No echo prompt for password
import crypt # Many Crypt functions

# Constant time Hash comepare that prevents the raw from ever being in memory
from hmac import compare_digest as comp_hash 

# Default config directory
CONFIGFILE = pathlib.Path('~/.secure_drop/config').expanduser()

def main():
    # Run Registration if not already done
    if (not isRegistered()):
        register()
        cleanUpAndExit()

    # Ask the user for login credentials
    # login()

    # Enter Custom SubShell defined be Shell class
    Shell().cmdloop()
    
# Custom Shell class, Defines options avaiable from command line
# Has built in help command which prints the text in first line
class Shell(cmd.Cmd):
    intro = ''
    prompt = 'Secure_Drop> '

    def do_exit(self, args):
        'Exit the program'
        cleanUpAndExit()
    def do_add(self, args):
        'Add a new contact'
        print('Add') # TODO stub
    def do_list(self, args):
        'List all online contacts'
        print('list') # TODO stub
    def do_send(self, args):
        'Transfer a file to contact'
        print('send') # TODO stub


# Find if a user is already registered
# Done by checking the config file and seeing if it contains credentials
def isRegistered():
    config = readConfig()

    # Ask for forgiveness not permission
    # ? Only checks for the existence of credentials not the validity of credentials,
    # ? is this good enough?
    try:
        config['Cred']['name']
        config['Cred']['email']
        config['Cred']['password']

        return True
    except KeyError: # Key does not exist in file
        return False
    

# Prompt the user for registration credentials, save to config if valid
def register():
    print('Register')

    name = input('Enter your full name: ')
    email = input('Enter your email address: ')
    password = cryptPassword(getpass.getpass('Enter your password: '))
    if (not checkPassword(getpass.getpass('Re-enter your password: '), password)):
        exit('Password Mismatch, Registration cancelled')

    print('Registration Successful')

    # Save credentials to config
    config = readConfig()

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

def readConfig():
    config = configparser.ConfigParser()
    if (CONFIGFILE.exists()):
        with open(CONFIGFILE, "r") as fp:
            config.read_file(fp)
    return config

def writeConfig(config):
    with open(CONFIGFILE, "w+") as fp:
        config.write(fp)
    
# Clean exit of subshell
def cleanUpAndExit():
    print('Exit SecureDrop')
    exit(0)

# Check to see if we are in a module or the main application
# If main, run main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Force closing the application due to SIG')
