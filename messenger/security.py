# ---------------------------
#Fichier : security.py
#Date : 14.10.2020
#But :
#Remarque :
#------------------------------
import random, string, base64

from flask_scrypt import generate_random_salt, generate_password_hash, check_password_hash, debase64, enbase64

SCRYPT_N = 65536
SCRYPT_SALT_LEN = 16
API_ID_LEN = 24

def implode(pw_hash, salt, N):
    """
    Implodes the given hash and its arguments into a string

    :param pw_hash: password hash
    :param salt: scrypt salt
    :param N: scrypt N factor
    :returns: hash string with arguments in order (N,salt,hash)
    """
    return '$' + str(N) + '$' + salt + '$' + pw_hash

def explode(hashstr):
    """
    Explodes a hash string whose values are separated by '$' into an array

    :param hashstr: hash string to explode
    :returns: elements of the given hash string as an array
    """

    indexes = [pos for pos, char in enumerate(hashstr) if char == '$']
    N = hashstr[indexes[0]+1:indexes[1]]
    salt = hashstr[indexes[1]+1:indexes[2]]
    pw_hash = hashstr[indexes[2]+1:]
    return [pw_hash, salt, N]

def hash_pw(password):
    """
    Hashes the given password using scrypt and a random salt

    :param password: password to hash
    :returns: hashed password with arguments
    """

    salt = generate_random_salt(SCRYPT_SALT_LEN)
    pw_hash = generate_password_hash(password, salt, N=SCRYPT_N)
    return implode(pw_hash.decode('ASCII'), salt.decode('ASCII'), SCRYPT_N)

def check_pw(password, pw_hash):
    """
    Checks whether the specified password and parameters match the given hash

    :param password: password to check
    :param pw_hash: hash string to compare with
    :returns: True if the password is correct, else False
    """

    hashvars = explode(pw_hash)
    return check_password_hash(
        str(password),
        str.encode(hashvars[0]),
        str.encode(hashvars[1]),
        int(hashvars[2])
    )

def gen_rand_string(prefix=None):
    """
    Generates a random string of 24 characters (alphanumeric case-sensitive)

    :param prefix: prefix to append to the random string
    :returns: random string of 24 alphanumeric characters (case-sensitive)
    """
    return (prefix + '_' if prefix != None else '') + ''.join(
        random.SystemRandom().choice(
            string.ascii_letters + string.digits
        ) for _ in range(API_ID_LEN)
    )
