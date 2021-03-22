import os
import click
import requests
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--order-id", type=str, required=True, help="a single order Id, or multiple orderId separated by comma")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, order_id, verbose):

    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    path = "v2/futures/order/status"
    url = f"{host}/{group}/api/pro/" + path

    ts = utc_timestamp()
    query = dict(orderId=order_id)

    if verbose:
        print(f"url: {url}")
        pprint(query)

    headers = make_auth_headers(ts, path, apikey, secret)
    res = requests.get(url, headers=headers, params=query)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    run()
