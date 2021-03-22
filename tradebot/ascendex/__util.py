import base64
import hashlib
import hmac
import time

from decimal import Decimal

from .__data_class_core import *


def hashing(query_string, secret: str):
    msg = bytearray(query_string.encode("utf-8"))
    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, msg, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
    return signature_b64


def get_timestamp():
    return int(time.time() * 1000)


def sign(msg, secret):
    msg = bytearray(msg.encode("utf-8"))
    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, msg, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
    return signature_b64


def make_auth_headers(timestamp, path, apikey, secret):
    # convert timestamp to string
    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode("utf-8")
    elif isinstance(timestamp, int):
        timestamp = str(timestamp)

    msg = f"{timestamp}+{path}"

    header = {
        "x-auth-key": apikey,
        "x-auth-signature": sign(msg, secret),
        "x-auth-timestamp": timestamp,
    }

    return header
