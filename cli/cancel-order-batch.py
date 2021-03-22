import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *

@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex-sandbox", help="specify the bot to use")
@click.option("--symbol", type=str, default='BTC-PERP')
@click.option("--order-id", type=str, required=True)
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, symbol, order_id, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/order/batch"

    ts = utc_timestamp()

    vs = symbol.split(',')
    vi = order_id.split(',')
    num = max(len(vs), len(vi))

    I = lambda s: s * (num // len(s))

    orders_to_cancel = {"orders":[]}
    for (s, i) in zip(I(vs), I(vi)) :
        orders_to_cancel["orders"].append(dict(
            id = uuid32(),
            time = ts,
            symbol = s,
            orderId = i
        ))

    if verbose:
        print(f"url: {url}")
        pprint(orders_to_cancel)

    headers = make_auth_headers(ts, "v2/futures/order/batch", apikey, secret)
    res = requests.delete(url, headers=headers, json=orders_to_cancel)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))



if __name__ == "__main__":
    run()
