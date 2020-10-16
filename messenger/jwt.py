# ---------------------------
#Fichier : jwt.py
#Date : 14.10.2020
#But :
#Remarque :
#------------------------------

import json, base64, hmac

from flask import request

from messenger import APP

# TODO handle malformed jwt

ENCODING = 'ascii'
HEADER = {
  'alg': 'HS256',
  'typ': 'JWT'
}

def jwt_encode(payload: dict, header=HEADER) -> str:
    """
    Create an RFC7519-compliant JWT (JSON Web Token)
    using the given payload and header.

    Uses `APP.secret_key` as HMAC key.

    :param payload: JWT payload
    :param header: JWT header
    :return: corresponding JWT
    """
    signature_message = '{}.{}'.format(
        b64pack(header),
        b64pack(payload)
    )

    signature = base64.b64encode(
        hmac.new(
            key=APP.secret_key.encode(ENCODING),
            msg=signature_message.encode(ENCODING),
            digestmod='SHA256'
        ).digest()
    ).decode('ascii')

    return '{}.{}'.format(
        signature_message,
        signature
    )

def jwt_decode(jwt: str) -> dict:
    """
    Verifies that the given JWT has been signed with
    `APP.secret_key`

    :param jwt: JWT to verify
    :return: JWT payload if signature is valid, else None
    """
    # TODO handle malformed jwt

    header, payload, signature = jwt.split('.')

    header = b64unpack(header)
    payload = b64unpack(payload)

    own_jwt = jwt_encode(payload, header)

    if hmac.compare_digest(own_jwt, jwt):
        return payload
    return None

def b64pack(data: dict) -> str:
    """
    Converts the given dict to a URL-safe base64 format

    :param data: JSON to transform
    :return: URL-safe base64 representation of `data`
    """
    return base64.b64encode(
        json.dumps(
            data,
            separators=(',', ':')
        ).encode(ENCODING)
    ).decode(ENCODING)

def b64unpack(data: str) -> dict:
    """
    Converts the URL-safe base64 data to a dict

    :param data: URL-safe base64 data to transform
    :return: dict representation of `data`
    """
    return json.loads(
        base64.b64decode(
            data
        ).decode(ENCODING)
    )

def get_current_jwt():
    """
    Return the JWT in the current request

    :return: JWT in current request
    """
    return jwt_decode(request.cookies.get('auth'))
