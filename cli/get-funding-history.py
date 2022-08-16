import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--symbol", type=str, default=None, help="symbol: BTCUSDT")
@click.option("--page", type=int, default=1, help="")
@click.option("--pagesize", type=int, default=20, help="")
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option('--verbose/--no-verbose', default=False)
def run(symbol, page, pagesize, config, botname, verbose):
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/funding-payments"

    req_params = dict(page=page, pageSize=pagesize)
    if symbol:
        req_params['symbol'] = symbol

    ts = utc_timestamp()
    headers = make_auth_headers(ts, "v2/futures/funding-payments", apikey, secret)

    if verbose:
        print(f"url = {url}")

    res = requests.get(url, headers=headers, params=req_params)
    # import ipdb; ipdb.set_trace()
    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))

    if verbose:
        pprint(res.headers)


if __name__ == "__main__":
    run()
