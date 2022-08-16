import os
import sys
import json
import time
import hmac, hashlib, base64
import random, string
import json
import yaml


def load_config(fname, exchange):
    with open(fname, "r") as config_file:
        if fname.endswith(".yaml"):
            return yaml.load(config_file, Loader=yaml.FullLoader)[exchange]
        else:
            return json.load(config_file)[exchange]


def check_sys_version():
    if not sys.version_info >= (3,5):
        print("Error: Python 3.5+ required")
        sys.exit(1)


def get_config_or_default(config):
    if config is None or not os.path.isfile(config):
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "conf.yaml")
        print(f"Config file is not specified, use {config}")
    return config


def uuid32():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))


def utc_timestamp():
    return int(round(time.time() * 1e3))


def sign(msg, secret):
    msg = bytearray(msg.encode("utf-8"))
    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, msg, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
    return signature_b64


def make_auth_headers(timestamp, path, apikey, secret, coid=None): 
    # convert timestamp to string   
    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode("utf-8")
    elif isinstance(timestamp, int):
        timestamp = str(timestamp)
    
    if coid is None:
        msg = f"{timestamp}+{path}"
    else:
        msg = f"{timestamp}+{path}+{coid}"
    
    header = {
        "x-auth-key": apikey,
        "x-auth-signature": sign(msg, secret),
        "x-auth-timestamp": timestamp,
    }
    
    if coid is not None:
        header["x-auth-coid"] = coid
    return header


def parse_response(res):
    if res is None:
        return None 
    elif res.status_code == 200:
        obj = json.loads(res.text)
        return obj
    else:
        print(f"request failed, error code = {res.status_code}")
        print(res.text)


def gen_server_order_id(account_id, symbol, side, cl_order_id, ts, order_src='a'):
    """
    Server order generator based on user info and input.
    :param account_id: account id
    :param symbol: product symbol
    :param side: buy or sell
    :param cl_order_id: user random digital and number id
    :param ts: order timestamp
    :param order_src: 'a' for rest api order, 's' for websocket order.
    :return: order id of length 32
    """
    h = hashlib.new("md5")
    h.update((str(ts) + account_id + symbol + side[0].lower() + cl_order_id).encode("utf-8"))
    return (format(ts, 'x')[:11] + order_src + account_id[-12:] + h.hexdigest())[:32]
