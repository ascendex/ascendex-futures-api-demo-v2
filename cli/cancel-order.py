import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *

@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--order-id", type=str, required=True, help="a single order Id")
@click.option("--symbol", type=str, default='BTC-PERP')
@click.option("--resp-inst", type=click.Choice(['ACK', 'ACCEPT', 'DONE']), default="ACCEPT")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, order_id, symbol, resp_inst, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/order"

    ts = utc_timestamp()
    cancelOrder = dict(
        id = 'abcd1234abcd1234', #uuid32(),
        orderId = order_id,
        symbol = symbol,
        time = ts,
        respInst = resp_inst,
    )

    if verbose:
        print(f"url: {url}")
        print(f"order: {cancelOrder}")

    headers = make_auth_headers(ts, "v2/futures/order", apikey, secret)
    res = requests.delete(url, headers=headers, json=cancelOrder)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))



if __name__ == "__main__":
    run()
