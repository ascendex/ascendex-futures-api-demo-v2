import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--asset", type=str, default='BTC')
@click.option("--amount", type=str, default=1, help="0.1")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, asset, amount, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/transfer/deposit"

    ts = utc_timestamp()
    requestBody = dict(
        asset = asset,
        amount = amount
    )

    if verbose:
        print(f"url: {url}")
        print(f"requestBody: {requestBody}")

    headers = make_auth_headers(ts, "v2/futures/transfer/deposit", apikey, secret)
    res = requests.post(url, headers=headers, json=requestBody)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))

if __name__ == "__main__":
    run()
