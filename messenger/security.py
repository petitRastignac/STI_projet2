# ---------------------------
#Fichier : security.py
#Date : 14.10.2020
#But :
#Remarque :
#------------------------------
import random, string, base64, hmac


SCRYPT_N = 65536
SCRYPT_SALT_LEN = 16
API_ID_LEN = 24

def implode(pw_hash, salt):
    """
    Implodes the given hash and its arguments into a string

    :param pw_hash: password hash
    :param salt: hash salt
    :returns: hash string with arguments in order (salt,hash)
    """
    return '$' + salt + '$' + pw_hash

def explode(hashstr):
    """
    Explodes a hash string whose values are separated by '$' into an array

    :param hashstr: hash string to explode
    :returns: elements of the given hash string as an array
    """

    return hashstr.split('$')

def hash_pw(password):
    """
    Hashes the given password using scrypt and a random salt

    :param password: password to hash
    :returns: hashed password with arguments
    """

    salt = gen_rand_string()
    pw_hash = base64.b64encode(
        hmac.new(
            key=salt.encode('utf8'),
            msg=password.encode('utf8'),
            digestmod='SHA256'
        ).digest()
    ).decode('utf8')

    return implode(pw_hash, salt)

def check_pw(password, pw_hash):
    """
    Checks whether the specified password and parameters match the given hash

    :param password: password to check
    :param pw_hash: hash string to compare with
    :returns: True if the password is correct, else False
    """

    hashvars = explode(pw_hash)
    mac = base64.b64decode(pw_hash)

    return hmac.compare_digest(hashvars[2].encode('utf8'), base64.b64encode(hmac.new(
        key=hashvars[1].encode('utf8'),
        msg=password.encode('utf8'),
        digestmod='SHA256'
    ).digest()))

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
