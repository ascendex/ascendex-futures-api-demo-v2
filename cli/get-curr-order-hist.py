import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *

@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--symbol", type=str, default=None)
@click.option("--n", type=int, default=None)
@click.option("--executed-only/--no-executed-only", default=False)
@click.option("--verbose/--no-verbose", default=False)
def run(config, botname, symbol, n, executed_only, verbose):

    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "v2/futures/order/hist/current", apikey, secret)
    url = f"{host}/{group}/api/pro/v2/futures/order/hist/current"

    query = dict(symbol=symbol, n=n, executedOnly=executed_only)

    if verbose:
        print(f"Using url: {url}")
        print(f"query: {query}")

    res = requests.get(url, headers=headers, params=query)
    pprint(parse_response(res))


if __name__ == "__main__":
    run()