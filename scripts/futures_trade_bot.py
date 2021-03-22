import logging
import sys
import asyncio
import json
import random

import click
from apscheduler.schedulers.background import BackgroundScheduler
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
# Local imports
from tradebot import load_config
from tradebot.ascendex import *
from pytz import utc
from quart import Quart

risk_engine: FuturesRiskEngine = None
api: AscendExApi = None

def create_protocol(apikey, secret):
    scheduler = BackgroundScheduler(timezone=utc)

    class MyClientProtocol(WebSocketClientProtocol):
        count = 0
        health = 2

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def schedule_ping(self):
            def aux():
                self.health = self.health - 1
                if self.health <= 0:
                    logging.critical("Stop WebSocket stream because the remote server is unresponsive")
                    sys.exit(1)
                self.send_sliently('{"op":"ping"}')

            scheduler.add_job(aux, 'interval', seconds=30, id='send_ping')

        def onConnect(self, response):
            print("Server connected: {0}".format(response.peer))

        def onOpen(self):
            self.schedule_ping()

            def heartbeat_actions():
                print("heartbeat")
                self.send("Hello world")

            # scheduler.add_job(heartbeat_actions, 'interval', seconds=5, id='heartbeat')

            scheduler.start()
            self.authenticate()

            # self.send("""{"op":"sub","id":"abc123456","ch":"depth-realtime:BTC-PERP"}""")
            # self.send("""{"op":"sub","id":"abc123456","ch":"bbo:BTC-PERP"}""")
            # self.send("""{"op":"sub","id":"abc123456","ch":"futures-pricing-data"}""")
            # self.send("""{"op":"sub","id":"abc123456","ch":"futures-order"}""")
            # self.send("""{"op":"sub","id":"abc123456","ch":"futures-account-update"}""")
            # self.send("""{"op":"req","id":"abc123456","action":"futures-account-snapshot"}""")
            # self.send("""{"op":"req","id":"abc123456","action":"futures-open-orders","args": {"symbol":"BTC-PERP"}}""")
            # self.send("""{"op":"req","id":"abc123456","action":"depth-snapshot-top100", "args": {"symbol":"BTC-PERP"} }""")
            # self.send("""{"op":"req","id":"abc123456","action":"depth-snapshot-realtime", "args": {"symbol":"BTC-PERP"} }""")
            # self.send("""{"op":"req","action":"barhist","id":"abc123456","args":{"symbol":"BTC-PERP","interval":"1d","from":1579427383528,"to":1610531443528,"v":null}}""")

            # self.send("""{"op":"req","action":"place-order","id":"sampleRequestId","ac":"futures","args":{"id":"sampleOrderId","symbol":"BTC-PERP","orderPrice":"40000","orderQty":"0.01","orderType":"limit","side":"buy"}}""")

            # self.send("""{"op":"req","action":"cancel-all","ac":"futures","id":"sampleRequestId","args":{"symbol":"BTC-PERP"}}""")

            print("WebSocket connection open.")

        def onMessage(self, payload, isBinary):
            global risk_engine

            self.count = self.count + 1
            self.health = 2
            if isBinary:
                print("Binary message received: {0} bytes".format(len(payload)))
            else:
                obj = json.loads(payload.decode('utf8'))
                if isinstance(obj, list):
                    print("RECV::: " + payload.decode("utf8"))
                    return

                m = obj.get('m', '')

                if m == "pong":
                    return

                elif m == "futures-pricing-data-batch":
                    for x in obj['data']:
                        risk_engine.add_pricing_data(FuturesPricingData(**x))

                elif m == "bbo":
                    risk_engine.add_bbo(Bbo(**obj))

                elif m == "futures-ref-price":
                    for x in obj['data']:
                        risk_engine.add_ref_price(RefPrice(**x))

                elif m == "futures-account-snapshot" or m == "futures-account-update":
                    account_position = FuturesAccountPosition(**obj)
                    risk_engine.update_account_position(account_position)

                else:
                    print("RECV:: " + json.dumps(obj))

        def onClose(self, wasClean, code, reason):
            print("WebSocket connection closed: {0}".format(reason))

        def authenticate(self):
            ts = get_timestamp()
            prehash_str = f"{ts}+v2/stream"
            sig = hashing(prehash_str, secret)
            self.send(f"""{{"op":"auth","id":"auth123","t":"{ts}","key":"{apikey}","sig":"{sig}"}}""")

        def send(self, msg):
            print("SEND::: " + msg)
            self.sendMessage(msg.encode('utf-8'))

        def send_sliently(self, msg):
            self.sendMessage(msg.encode('utf-8'))

    return MyClientProtocol


app = Quart(__name__)

@app.route("/bbo")
async def bbo():
    d = risk_engine.bbo_by_symbol
    return {k: JsonConverter(v).to_json() for k, v in d.items()}

@app.route("/auth")
async def auth():
    d = risk_engine.auth
    return JsonConverter(d).to_json()

@app.route("/ref-price")
async def ref_price():
    d = risk_engine.ref_price_by_asset
    return {k: JsonConverter(v).to_json() for k, v in d.items()}

@app.route("/pricing-data")
async def pricing_data():
    d = risk_engine.pricing_data_by_symbol
    return {k: JsonConverter(v).to_json() for k, v in d.items()}

@app.route("/position")
async def position():
    return JsonConverter(risk_engine.account_position).to_json()

@app.route('/api/position')
async def api_position():
    return JsonConverter(api.get_futures_position(), api.error).to_json()

@app.route("/total-margin")
async def total_margin():
    """总保证金 Total Margin"""
    return float2json(risk_engine.total_margin, "total_margin", risk_engine.error)

@app.route("/upnl")
async def unrealized_pnl():
    """未实现盈亏 Unrealized PnL"""
    return float2json(risk_engine.unrealized_pnl, "unrealized_pnl", risk_engine.error)

@app.route("/cpn")
async def contract_position_notional():
    """合约仓位价值 Contract Position Notional"""
    return JsonConverter(risk_engine.contract_position_notional, risk_engine.error).to_json()

@app.route("/position-margin")
async def margin_requirement():
    return JsonConverter(risk_engine.position_margin, risk_engine.error).to_json()

@app.route("/change-margin-type/<symbol>/<marginType>")
async def change_margin_type(symbol, marginType):
    tp = MarginType._member_map_.get(marginType.lower())
    if tp is None:
        m = "invalid margin type: " + marginType + ". Allowed values: " + ", ".join(MarginType._member_names_)
        return dict(error=m)
    else:
        return JsonConverter(api.change_margin_type(symbol, tp), api.error).to_json()

@app.route("/api/change-iso-position-margin/<symbol>/<amount>")
async def api_change_iso_position_margin(symbol, amount):
    return JsonConverter(api.change_ios_position_margin(symbol, amount), api.error).to_json()

@app.route("/api/change-leverage/<symbol>/<int:leverage>")
async def change_leverage(symbol, leverage):
    return JsonConverter(api.change_leverage(symbol, leverage), api.error).to_json()

@app.route("/api/futures/transfer/deposit/<asset>/<amount>")
async def api_deposit_to_futures(asset, amount):
    return JsonConverter(api.deposit_to_futures(asset, amount), api.error).to_json()

@app.route("/api/futures/transfer/withdraw/<asset>/<amount>")
async def api_withdraw_from_futures(asset, amount):
    return JsonConverter(api.withdraw_from_futures(asset, amount), api.error).to_json()

@app.route("/api/futures/free-margin")
async def api_free_margin():
    return JsonConverter(api.free_margin(), api.error).to_json()

@app.route("/random-maker-order/<symbol>/<side>")
async def random_maker_order(symbol, side):
    sd = OrderSide._member_map_.get(side.lower())
    if sd is None:
        return dict(error="invalid order side: " + side + ". Allowed values: " + ", ".join(OrderSide._member_names_))
    else:
        return JsonConverter(risk_engine.place_random_order(symbol, sd, is_maker=True), risk_engine.error).to_json()

@app.route("/random-taker-order/<symbol>/<side>")
async def random_taker_order(symbol, side):
    sd = OrderSide._member_map_.get(side.lower())
    if sd is None:
        return dict(error="invalid order side: " + side + ". Allowed values: " + ", ".join(OrderSide._member_names_))
    else:
        return JsonConverter(risk_engine.place_random_order(symbol, sd, is_maker=False), risk_engine.error).to_json()

@app.route('/api/open-order', defaults={'symbol': None})
@app.route('/api/open-order/<symbol>')
async def api_open_order(symbol):
    return JsonConverter(api.open_orders(symbol), api.error).to_json()

@app.route('/open-order', defaults={'symbol': None})
@app.route('/open-order/<symbol>')
async def open_order(symbol):
    return JsonConverter(risk_engine.open_orders(symbol), api.error).to_json()



@click.command()
@click.option("--config", type=str, default="sample-conf.yaml")
@click.option("--botname", type=click.Choice(["ascendex", "ascendex-sandbox", "ascendex-local", "ascendex-api-test"]), default="ascendex-sandbox")
@click.option("--log-level", type=click.Choice(["debug", "info", "warning", "error", "critical"]), default="warning")
@click.option("--server-port", type=int, default=5000)
def run(config, botname, log_level, server_port):
    logging.basicConfig(level=getattr(logging, log_level.upper()))

    cfg = load_config(config, botname)
    host = cfg['base-url']
    group = cfg["group"]
    apikey = cfg['apikey']
    secret = cfg['secret']
    wss_endpoint = cfg['wss-endpoint']
    ssl = cfg['ssl']
    port = int(cfg.get('wss-port')) or 443

    global risk_engine, api
    risk_engine = FuturesRiskEngine(host, apikey, secret).initialize()
    api = risk_engine.api

    if ssl:
        connect_str = f"wss://{wss_endpoint}:{port}/{group}/api/pro/v2/stream"
    else:
        connect_str = f"ws://{wss_endpoint}:{port}/{group}/api/pro/v2/stream"

    print("Connection string " + connect_str)
    factory = WebSocketClientFactory(connect_str)
    factory.protocol = create_protocol(apikey, secret)

    loop = asyncio.get_event_loop()

    coro_wss = loop.create_connection(factory, wss_endpoint, port, ssl=ssl)
    coro_server = app.run_task(port=server_port)

    async def multitask():
        # Assign a single task
        task1 = loop.create_task(coro_wss)
        task2 = loop.create_task(coro_server)
        # Run the task asynchronously
        await asyncio.wait([task1, task2])

    # loop.run_until_complete(coro_wss)
    loop.run_until_complete(multitask())

    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    run()

