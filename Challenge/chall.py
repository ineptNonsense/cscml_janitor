from random import randint, random
import os, time

DIGITS = '0123456789'
LETTERS = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'

TOKEN_LENGTH = 16
PASSWORD_LENGTH = 40

debug = None

def main():
    print('################################')
    print('# WELCOME TO SUPER_AUTH,       #')
    print('# THE INCREDIBLY SAFE SERVER   #')
    print('################################')
    print()
    print('> WARNING:')
    print('> The server is not yet working properly.')
    print('> Please proceed with caution.')
    print()

    print('> Do you have a SUPER_AUTH token? (Y/N)', end=' ')
    text = input()
    if not text.upper() == 'Y':
        token = generate_random_token()
        init_random_password(token)
        print('> Your SUPER_AUTH token is:')
        print('######################')
        print('## {} ##'.format(token))
        print('######################')
        print('> A password has been generated for your token.')
        print('> Please consult your local Admin to recieve your password.')
        print_admin_email() # TO-DO: Ask the web admin for his email.
        return

    print('> Please input your token:', end=' ')
    token = input()
    if not does_token_exist(token):
        print('> Your token seems to be invalid. Sure you typed it in correctly?')
        print('> Please consult your local Admin to recieve your password.')
        print_admin_email() # TO-DO: Ask the web admin for his email.
        return

    print('> Please input your password:', end=' ')
    key_test = parse_input(input())

    if auth(token, key_test):
        print(open('Files/flag.txt', 'rb').read())
    else:
        print('> Authentication failed.')
        print('> Please recheck your credentials and try again.')

def print_admin_email():
    """
    ###############################
    ## BOB LOOK HERE ALREADY OMG ##
    ###############################

    #################################
    ## BOB COME ON THIS ISNT FUNNY ##
    #################################

    ############################
    ## IT'S BEEN A MONTH, BOB ##
    ############################
    """
    # Bob, when you open this file, please fill in your email.
    # Like, right here.
    # Nobody's been able to log-in for the past year,
    # and we're getting tired of it.
    bob_email = '???@gmail.com'
    print('> You can contact him at: {}'.format(bob_email))

def get_pass_file(token):
    return 'Tokens/{}.pass'.format(token)

def generate_random_token():
    token = ''.join(chr(ord('A') + randint(0, 25) + 32*randint(0, 1)) for n in range(TOKEN_LENGTH))
    return token

def does_token_exist(token):
    # Making sure the token looks valid:
    if len(token) != TOKEN_LENGTH:
        return False
    for c in token:
        if not c in LETTERS:
            return False
    # Checking whether a password file exists:
    return os.path.exists(get_pass_file(token))

def auth(token, key_test):
    """
    Try and authenticate a user's login.
    """
    x = None
    
    try:
        x = get_pass_file(token) # Returns None if no password was found.
        key_target = read_password(x)

        if len(key_test) != len(key_target):
            return False

        success = True
        print('> Beginning authentication...')
        for i in range(len(key_target)):
            x = local_hash(key_target, i)
            x -= local_hash(key_test, i)
            if abs(x) > 0.00001:
                # The hashes are different.
                success = False
        return success
    
    except Exception as e:
        # If reading the file failed:
        if not x:
            print("> Password file doesn't exist.")
            print("> Resetting random password...")
            init_random_password(token)
        else:
            print("> Failed reading file {}.".format(x))
            print("> Maybe the server is busy. Wait a few seconds, then try again.")

def local_hash(arr, ind):
    """
    ALL CREDIT GOES TO THE CREATORS OF SUPER_AUTH
    PLEASE DO NOT STEAL OR WE WILL SUE
    """
    
    """
    Do a local hash on the values of arr, at index ind.
    Doing the hash locally makes hash-checking more efficient.
    (You don't have to calculate the entire hash to see that two hashes are different)
    """
    objs = [arr[ind]]
    for i in [-16, 0, 16]:
        for j in [-1, 0, 1]:
            x = ind + i + j
            if 0 <= x < len(arr) and ind // 16 == (ind + j) // 16 and not i == j == 0:
                objs.append(arr[x] + 1)
    
    h = objs[0]
    h += randomize(h)
    h *= harmonic_average(objs)

    return h

def harmonic_average(lst):
    """
    Return the harmonic average of values in a list.
    """
    global debug
    debug = lst
    return len(lst) / sum(1/x for x in lst)

def is_positive_digit(s):
    """
    Checks whether (s) is a string of digits depicting
    a positive (and thus non-zero) integer.
    """

    # Checking that (s) is a string of digits:
    for c in s:
        if not c in DIGITS:
            return False

    # Checking that (s) is not equal to zero:
    if set(s) == set('0'):
        return False
    
    return True

def parse_digit(s):
    """
    Converts the string (s) into an integer.
    """
    total = 0
    for c in s:
        total *= 10
        total += ord(c) - ord('0') # Parse a single-digit number as an integer.
    return total

def parse_input(s):
    """
    Parse the user's input.
    """
    digits = s.split(' ')

    for d in digits:
        if not is_positive_digit(d):
            return []

    return [parse_digit(d) for d in digits]

def init_random_password(token):
    """
    Create a random password for a new SUPER_AUTH user,
    and save it in the appropriate file.
    """
    lst = (list(range(6))*43)[:256]
    lst.sort(key=lambda x:random())
    buff = bytes(lst)

    # Save password
    with open(get_pass_file(token), 'wb') as file:
        file.write(buff)
    
def read_as_bits(b):
    """
    Takes a list of bytes, and converts it to a list of bits (8 times as long)
    """
    assert type(b) == bytes
    return list(map(bool, b))

def read_password(pass_file):
    """
    Parse the password from a password file.
    """
    with open(pass_file, 'rb') as file:
        b = file.read()
    bits = read_as_bits(b)

    # In case any zeroes appeared in the password:
    for i in range(len(bits)):
        bits[i] += 1

    return bits

def randomize(i):
    #TO-DO: Implement later when you think of something.
    return -1

if __name__ == "__main__":
    print('[SESSION STARTING]')
    main()
    print('[SESSION ENDING]')
    
    time.sleep(1) # I don't remember why this is here, but I'm going to keep it anyway.
