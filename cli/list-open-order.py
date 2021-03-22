import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *

@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=click.Choice(["ascendex", "ascendex-sandbox"]), default="ascendex-sandbox", help="specify the bot to use")
@click.option("--symbol", type=str, default=None, help="symbol: BTC-PERP")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, symbol, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/order/open"
    
    ts = utc_timestamp()

    reqParams = dict()
    if symbol: reqParams['symbol'] = symbol  # specify symbol to list open orders

    if verbose:
        print(f"url: {url}")

    headers = make_auth_headers(ts, "v2/futures/order/open", apikey, secret)
    res = requests.get(url, headers=headers, params=reqParams)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))



if __name__ == "__main__":
    run()
