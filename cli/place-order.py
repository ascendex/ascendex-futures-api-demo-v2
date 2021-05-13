import os
import click
import requests
from pprint import pprint

# Local imports 
from util import *


all_exec_inst = [
    "Post", "ReduceOnly", "PostReduceOnly",
    "StopOnMarket", "StopOnMark", "StopOnRef",
    "PostStopMarket", "PostStopMark", "PostStopRef",
    "ReduceOnlyMarket", "ReduceOnlyMark", "ReduceOnlyRef",
    "PostReduceMarket", "PostReduceMark", "PostReduceRef",
    "OpenStopMkt", "OpenStopMark", "OpenStopRef",
    "OpenPostStopMkt", "OpenPostStopMark", "OpenPostStopRef",
]


@click.command()
@click.option("--config", type=str, default=None, help="path to the config file")
@click.option("--botname", type=str, default="ascendex", help="specify the bot to use")
@click.option("--symbol", type=str, default='BTC-PERP')
@click.option("--price", type=str, default='30000')
@click.option("--qty", type=str, default='0.1')
@click.option("--order-type", type=str, default="limit")
@click.option("--side", type=click.Choice(['buy', 'sell']), default='buy')
@click.option("--time-in-force", type=click.Choice(['GTC', 'IOC', 'IOO']), default="GTC")
@click.option("--reduce-only/--no-reduce-only", default=False)
@click.option("--post-only/--no-post-only", default=False)
@click.option("--exec-inst", type=click.Choice(all_exec_inst), default=None)
@click.option("--pos-stop-loss", type=str, default=None)
@click.option("--pos-take-profit", type=str, default=None)
@click.option("--resp-inst", type=click.Choice(['ACK', 'ACCEPT', 'DONE']), default="ACCEPT")
@click.option('--verbose/--no-verbose', default=False)
def run(config, botname, symbol, price, qty, order_type, side, time_in_force, reduce_only, post_only, exec_inst, pos_stop_loss, pos_take_profit, resp_inst, verbose):
    
    cfg = load_config(get_config_or_default(config), botname)

    host = cfg['base-url']
    group = cfg['group']
    apikey = cfg['apikey']
    secret = cfg['secret']

    url = f"{host}/{group}/api/pro/v2/futures/order"

    ts = utc_timestamp()
    order = dict(
        id = 'abcd1234abcd1234', #uuid32(),
        time = ts,
        symbol = symbol,
        orderPrice = str(price),
        orderQty = str(qty),
        orderType = order_type,
        side = side.lower(),
        timeInForce = time_in_force,
        reduceOnly = reduce_only,
        postOnly = post_only,
        execInst = exec_inst,
        posStopLossPrice = pos_stop_loss,
        posTakeProfitPrice = pos_take_profit,
        respInst = resp_inst,
    )

    if verbose:
        print(f"url: {url}")
        print(f"order: {order}")

    headers = make_auth_headers(ts, "v2/futures/order", apikey, secret)
    res = requests.post(url, headers=headers, json=order)

    data = parse_response(res)
    print(json.dumps(data, indent=4, sort_keys=True))



if __name__ == "__main__":
    run()
