import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--symbol", type=str, default='BTC-PERP')
@click.option("--price", type=str, default='30000')
@click.option("--qty", type=str, default='0.1')
@click.option("--order-type", type=str, default="limit")
@click.option("--side", type=click.Choice(['buy', 'sell']), default='buy')
@click.option("--resp-inst", type=click.Choice(['ACK', 'ACCEPT', 'DONE']), default="ACK")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, symbol, price, qty, order_type, side, resp_inst, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    path = "v2/futures/order/batch"
    url = f"{host}/{group}/api/pro/" + path

    ts = utc_timestamp()

    vs = symbol.split(',')
    vp = price.split(',')
    vq = qty.split(',')
    vt = order_type.split(',')
    vsd = side.split(',')
    vri= resp_inst.split(',')

    num = max(len(vs), len(vp), len(vq), len(vt), len(vsd), len(vri))

    I = lambda s: s * (num // len(s))

    orders_to_place = {"orders":[],}
    for (s, p, q, t, sd, ri) in zip(I(vs), I(vp), I(vq), I(vt), I(vsd), I(vri)):
        orders_to_place["orders"].append(dict(
            id = uuid32(),
            time = ts,
            symbol = s,
            orderPrice = str(p),
            orderQty = str(q),
            orderType = t,
            side = sd.lower(),
            respInst = ri,
        ))

    if verbose:
        print(f"url: {url}")
        pprint(orders_to_place)

    headers = make_auth_headers(ts, path, apikey, secret)
    res = requests.post(url, headers=headers, json=orders_to_place)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))


if __name__ == "__main__":
    run()

