import os
import click
import requests
from pprint import pprint

# Local imports
from util import *


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, verbose):

    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/api/pro/v2/account/info"

    ts = utc_timestamp()

    if verbose:
        print(f"url: {url}")

    headers = make_auth_headers(ts, "v2/account/info", apikey, secret)
    res = requests.get(url, headers=headers)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    run()
