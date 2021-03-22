import click
import time
import hashlib
import hmac
import base64
import asyncio    # pip3 install asyncio
import websockets # pip3 install websockets
import json

def hashing(message: str, secret: str) -> str:
    msg = bytearray(message.encode("utf-8"))
    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, msg, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
    return signature_b64

def get_timestamp() -> int:
    return int(time.time() * 1000)


async def websocket_auth_demo(uri):
    ts = get_timestamp()
    async with websockets.client.connect(uri) as websocket:
        await websocket.send("""{ "op": "sub", "id": "abc123", "ch":"trades:BTC-PERP" }""")
        while True:
            msg = await websocket.recv()
            obj = json.loads(msg)
            if obj['m'] == 'ping':
                print(msg)
                await websocket.send("""{ "op": "pong" }""")
            else:
                print(msg)

asyncio.get_event_loop().run_until_complete(
    websocket_auth_demo('wss://ascendex.io:443/api/pro/v2/stream'))

