So. Janitor. Let's break it down.

## 1. Baby Steps

As in any challenge, the first thing it'd make sense to do would be to open up the Python program and run it locally. See what happens.

```
[SESSION STARTING]
################################
# WELCOME TO SUPER_AUTH,       #
# THE INCREDIBLY SAFE SERVER   #
################################

> WARNING:
> The server is not yet working properly.
> Please proceed with caution.

> Do you have a SUPER_AUTH token? (Y/N)
```

Looks like we're asked for a token. But we don't have one. Let's go with no?

```
> Do you have a SUPER_AUTH token? (Y/N) n
> Your SUPER_AUTH token is:
######################
## ygGkbwEpjUoWKQxl ##
######################
> A password has been generated for your token.
> Please consult your local Admin to recieve your password.
> You can contact him at: ???@gmail.com
[SESSION ENDING]
```

Well that was useful. I can see a nice file named "ygGkbwEpjUoWKQxl.pass" was created under a folder labeled Tokens. Also, the program ended. Too bad. Let's restart, and this time say we have a token.  

Once we do this, we're immediately prompted to enter our token. Taking a quick look at the code behind this, looks like a relatively safe way (for now) to the program to separate user sessions.  

Let's remember our token, and use only it from now on. We won't be needing another.

```
[SESSION STARTING]
################################
# WELCOME TO SUPER_AUTH,       #
# THE INCREDIBLY SAFE SERVER   #
################################

> WARNING:
> The server is not yet working properly.
> Please proceed with caution.

> Do you have a SUPER_AUTH token? (Y/N) y
> Please input your token: ygGkbwEpjUoWKQxl
> Please input your password: 
```

Damn it. But we have no password.

```
> Please input your password: 12345
> Authentication failed.
> Please recheck your credentials and try again.
[SESSION ENDING]
```

Looks legit. Let's see what's going on behind the scenes.

## 2. A Quick Look-See

```python
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
```

Here's our main function. It gets called each time we run the program.  Here we see a few interesting methods being called:

- `init_random_password(token)` - Probably the method that created the ".pass" file we saw earlier.
- `parse_input(input)` - When we're asked for a password, this is the monster we're feeding.
- `auth(token, key_test)` - Scrolling a little lower in the program, I can see this method looks a tad bulky. Guess this is where we securely (*sorry, securely?*) make sure the server's password matches ours.

I think I'm interested in ` parse_input`. Let's check it out.

```python
def parse_input(s):
    """
    Parse the user's input.
    """
    digits = s.split(' ')

    for d in digits:
        if not is_positive_digit(d):
            return []

    return [parse_digit(d) for d in digits]
```

So our input gets split into blocks with the space character. Then we check that each digit is positive, and read them into a list. Sounds like the password we're expected to input is a list of positive integers.

Since `is_positive_digit` and `parse_digit` seem relevant, let's copy these methods as well:

```python
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
```

This feels fishy. Especially since the program actively avoids calling `int` on the user's input.  
A closer look reveals that `is_positive_digit` would return `True` on the empty string `""`.  
In fact, `parse_digit` would parse it as `0`, instead of raising an exception, as `int` would rather do.

And the best part is, that we can indeed pass an empty string, simply by putting two spaces in a row in our user input:  
For example, the input `"2 1  3"` would be split into blocks as `["2", "1", "", "3"]`, which would then be parsed as the list `[2, 1, 0, 3]`.

Cool. I'm satisfied for now. Let's go back to the list of methods we saw called during `main`. We have both `init_random_password` and `auth` to look at. I think we'll start with the first.

## 3. I don't know how to describe this code. It's just really bad.

```python
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
```

So this is the how our password was created. It's a list of bytes valued from 0 to 5 (inclusive), of length 256. Noting that `6 * 43 = 258 ≈ 256`, we can say that each value appears about an equal amount of times.  
Before we go look at `auth`, I can see that slightly under this method, we have another method named `read_password`. And it takes a parameter named `pass_file` as input. Could this be the method that reads the files `init_random_password` creates?

```python
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
```

Definitely looks like something that would take a password filename as input. We pass the bytes through `read_as_bits`, and then add 1 to each byte.  
Adding 1 seems like an odd design choice. Let's keep that in mind for later. What does `read_as_bits` do?

```python
def read_as_bits(b):
    """
    Takes a list of bytes, and converts it to a list of bits (8 times as long)
    """
    assert type(b) == bytes
    return list(map(bool, b))
```

Huh, okay.  
First of all, let me begin by saying that the thing the documentation says this method does is **nothing at all** like what the method actually does. Seems like this method takes a list of bytes (as we understand from `read_password`), and maps each non-zero byte to 1 (keeping the values of the zero bytes).  
This is degeneracy at its pique.

Together with `read_password`, what goes on is we read a list of bytes from a file, and turn them into a list of ones and twos - where ones appear wherever a 0-byte appeared in the password file, and twos appear everywhere else.

Putting that together with `init_random_password` : In the password file, it looks like we have bytes from 0 to 5, and about equal amounts of each. Effectively, when we read the file, we get a list of 256 integers, all ones and twos. (About 42 ones, and the rest are twos).

This is nothing at all like what I think this method claims to do. But oh well. Let's move on to the `auth` method.

## 4. When in Auth, do as the Auths would do.

As usual, we begin with a code block:

```python
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
```

This gets called with our token, and the value `key_test`, which a quick check shows us is the parsed password we gave as input.  
We can see that one of the first things this method does is call `read_password` on `get_pass_file`. It doesn't take long to make sure this reads precisely the password file that was created for us earlier. As we expected. This value is saved in `key_target`, and it looks like the rest of this method is dedicated to checking that `key_test` and `key_target` hold the same value. And it's done in a very convoluted way. I guess that makes it safer code? <sub>(haha nope)</sub>

At this point, I would like to experiment a little, and see what happens if I send a 0 in my `key_test` list. There must be a reason why `read_password` wanted to avoid zeroes so badly.

I sent some test passwords in. Looks like I need to make the parser take in 256 integers, otherwise the first conditional statement will return `False`, and that will be that. Putting in a double-space always returned a sort of error message, which interestingly, was different almost every time (depending on the index in which I inserted the double-space).

One sort of output looked like:

```
> Beginning authentication...
> Failed reading file 2.6999999999999997.
> Maybe the server is busy. Wait a few seconds, then try again.
> Authentication failed.
> Please recheck your credentials and try again.
[SESSION ENDING]
```

Where the float at the end of the second line varied from output to output. On the other hand, once in a while, I'd receive the second sort of error that `auth` seems to be able to print:

```
> Password file doesn't exist.
> Resetting random password...
```

At the moment, I think that what interests me is why weird fractions are printed. The error messages seem to be intended to correspond to the first two lines in the `try` clause, where we read a file name, put it in the variable `x`, and then parse its contents as the password. But wait! The same `x` makes an appearance a few lines later, inside the weird `for` loop that calls `local_hash`. What if the program crashes mid-loop, and we're leaking values of `x `? That would be cool, since it looks like `x` is being set to a hash of the target password. Maybe leaks of this sort can give us enough info to reconstruct the password?

The `local_hash` is checked for each character in both the target password and our input, and the program goes through all of them, before releasing its verdict on whether the passwords are different. This is good for us, as it means we can try crash the program during any index, without having to worry about knowing the previous characters of the password beforehand.

I think it's high time we take a proper look at `local_hash`. Who's with me?

## 5. A foolproof recipe for hash browns

```python
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
```

Reading this, it looks like `local_hash` doesn't really do anything complex. Given an index `ind` (from 0 to 255), we:

1. Consider our password as a 16x16 matrix (in which we consider the value at position `(ind % 16, ind // 16)`.
   Denote by `x` the value of the password at this index.
2. Make a list of the password values at each of the 8 cells that are neighbors to our cell (by edge or corner)  
   (if our cell is at the edge of the grid, simply take less cells in the list). Then add one to each cell. Then add the `x` to the list.
3. Calculate the [Harmonic Average](https://en.wikipedia.org/wiki/Harmonic_mean) of the values in the list.
4. Multiply the result by `x - 1`  (because `randomize` returns `-1`), and return that result.

Now we see what's making the program crash when we enter a zero - we crash precisely on the index where we put it, since calculating the harmonic average makes us divide by zero. This means that when we input a list that has a zero at an index `i`, we get to leak the value of `local_hash(target_pass, i)`.

Unless, of course, `local_hash(target_pass, i) == 0`. This can happen only if `target_pass[i] == 1`, because then in step 4 of calculating `local_hash`, we have `x == 1` and thus `x - 1 == 0`.  Which we multiply our result by, before returning. Cool.

## 5. Drumroll

We figured out how to make the program crash at any index. If at that index the value of the server's password was 2, we get to see the `local_hash` at that point. Otherwise the password resets, which sucks, because if we could leak the hash at every index, we'd probably be able to reconstruct the password (with a little sweat and some solving of linear equations). Guess we won't do that.

Looks like we'll need to somehow leak hashes only belonging to indices where the password is equal to 2. But also, let's think for a moment about what information we get from leaking part of the hash:

Say the password at index `(x, y)` (when looking at the password as a grid) is equal to 2. And say that out of it's 8 surrounding neighbors (assuming `(x, y)` is not on an edge) there are `k` neighbors valued 1, and `8 - k` neighbors valued 2. The value we leak is therefore: `8 / ((9 - k) * (1 / 2) + k * (1 / 1)) `. It is quite easy to, from this value, deduce the value of `k`. (the calculation is slightly different, but we can do the same for cells on the edges of the 16x16 grid as well).

Basically, when we leak the index of a hash, we find out how many 1's are in the surrounding eight cells.

Effectively, we're playing a game of Minesweeper.

And that's it.

## 6. A Few Notes to Wrap Up

This repository also contains a small program that communicates with the server, if you'd like to feel like you're playing Minesweeper. If that interests you, take a look at `solution.py`.

Run this file in your favorite IDE. The API works as follows:

* Start out by calling `create_token()`. This makes a connection with the server, reads a token, and saves it for future use.
* Now, try calling, for instance `play(3, 4)`. This asks the server for the password hash at coordinate `(3, 4)`, calculates for you how many mines surround that spot, and prints the resulting board for you to see. (Remember, each coordinate runs from 0 to 15)
  * If for some reason there are `0` bombs around the spot you picked,  
    the method will also contact the server and try mark all surrounding spots for you.  
    If that's the case, just wait a couple seconds. Or maybe longer.  
    Don't worry about it - the program is simply doing your job for you. :P
* Calling `mark(3, 4)` won't contact the server, but will instead mark the board for you with an `X` to remind you of a location of a mine.
  * You can call it again on a marked spot to unmark it, if you change your mind.
* When the board is completely filled (if you called `play` and `mark` enough times so that every single spot is filled), try calling `finished()`. This will parse the password for you, send it to the server, and print out the server's response.

Good luck!