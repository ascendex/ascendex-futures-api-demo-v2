import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *

@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--symbol", type=str, default=None, help="symbol: BTC-PERP")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, symbol, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/order/all"
    
    ts = utc_timestamp()
    cancelAllOrder = dict(
        symbol = symbol,
    )

    if verbose:
        print(f"url: {url}")
        print(f"order: {cancelAllOrder}")

    headers = make_auth_headers(ts, "v2/futures/order/all", apikey, secret)
    res = requests.delete(url, headers=headers, json=cancelAllOrder)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))



if __name__ == "__main__":
    run()
