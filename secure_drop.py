#!/usr/bin/env python3

# import os
import cmd # Supplies the subshell CMD prompt
import pathlib # Sane Path accessors/Validators
import configparser # .ini-ish file config accessor/generators
import getpass # No echo prompt for password
import crypt # Many Crypt functions
import argparse # Command Line Argument Parser
import logging # Logging tools

# RSA tools
from Cryptodome.PublicKey import RSA 

# Constant time Hash compare that prevents the raw from ever being in memory
from hmac import compare_digest as comp_hash 

logger = logging.getLogger('secure_drop')
logger.propagate = False

parser = argparse.ArgumentParser(description="Secure File Drop")
parser.add_argument('-c','--config', action='store', default='~/.config/secure_drop/config')

args = parser.parse_args()

ConfigPath = args.config

# Default config directory
CONFIGFILE = pathlib.Path(ConfigPath).expanduser()
CONFIGFILE.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
CONFIGFILE.touch(mode=0o700, exist_ok=True)

# import peerDetect

def main():
    # Run Registration if not already done
    if (not isRegistered()):
        register()
        cleanUpAndExit()

    # Ask the user for login credentials
    login()

    # Enter Custom SubShell defined be Shell class
    Shell().cmdloop()
    
# Custom Shell class, Defines options available from command line
# Has built in help command which prints the text in first line
class Shell(cmd.Cmd):
    intro = ''
    prompt = 'Secure_Drop> '

    def do_exit(self, args):
        'Exit the program'
        cleanUpAndExit()
    def do_add(self, args):
        'Add a new contact'
        addContact()
    def do_list(self, args):
        'List all online contacts'
        listOnlineContacts()
    def do_send(self, args):
        'Transfer a file to contact'
        sendFile()

def addContact():
    print('addContact') # TODO stub

    #Store in config file
    newName = input('Enter full name: ')
    newEmail = input('Enter email address: ')

    config = readConfig()
    name = config['Cred']['name']
    email = config['Cred']['email']
    
    if (name == newName ):
        print("Invalid User. User already existed.")
    
    else:
        config['Contacts ' + newName] = {
        'name':newName,
        'email':newEmail,
        }
        writeConfig(config)
        print("Contact added")

def listOnlineContacts():
    print('listOnlineContacts') # TODO stub

def sendFile():
    print('sendFile') # TODO stub

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
        config['Cred']['private_key']
        config['Cred']['public_key']

        return True
    except KeyError: # Key does not exist in file
        return False
    

# Prompt the user for registration credentials, save to config if valid
def register():
    print('Register')

    name = input('Enter your full name: ')
    email = input('Enter your email address: ')
    raw_password = getpass.getpass('Enter your password: ')
    password = cryptPassword(raw_password)
    if (not checkPassword(getpass.getpass('Re-enter your password: '), password)):
        exit('Password Mismatch, Registration cancelled')
        
    #Generate RSA Public/Private Key
    key = RSA.generate(2048)
    private_key = key.export_key(passphrase=raw_password, pkcs=8, protection='scryptAndAES128-CBC')
    public_key = key.publickey().export_key()
    del raw_password

    print('Registration Successful')

    # Save credentials to config
    config = readConfig()

    config['Cred'] = {
        'name':name,
        'email':email,
        'password':password,
        'public_key':public_key,
        'private_key':private_key}

    writeConfig(config)

def login():
    print('login')

    # ! Should not tell the user which part of the credential is invalid
    # ! Need to save some information generated from the password to use to
    # !     during the application run

    enteredEmail = input('Enter your email address: ')

    config = readConfig()

    email = config['Cred']['email']
    rawPassword = str

    if (email == enteredEmail):    
        password = config['Cred']['password']
        rawPassword = getpass.getpass('Enter your password: ')
        if (not checkPassword(rawPassword, password)):
            exit('Password Mismatch, Login cancelled')
    else:
        exit('User is not registered, Login cancelled')

    # If above checks pass, user is valid
    # Save login information to use in crypto functions

    UserName = config['Cred']['name']
    Email = config['Cred']['email']
    
    # key = RSA.import_key(config['Cred']['private_key'], passphrase=rawPassword)

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
        with open(CONFIGFILE, "r+") as fp:
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
