import click
import time
import hashlib
import hmac
import base64
import asyncio    # pip3 install asyncio
import websockets # pip3 install websockets

def hashing(message: str, secret: str) -> str:
    msg = bytearray(message.encode("utf-8"))
    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, msg, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
    return signature_b64

def get_timestamp() -> int:
    return int(time.time() * 1000)


async def websocket_auth_demo(uri):
    # this API key only works in the sandbox environment
    apikey = "YGfuHmCpSP98a4uxc4ajLvOliqtHRlrj" 
    secret = "5NupIDHZZ9Dvp6Rta6mrAKDoodWDUeI2TqDVhzxoaFKLLuUaqePPGmfH9LSiySSy"
    ts = get_timestamp()
    message = str(ts) + "+v2/stream"
    sig = hashing(message, secret)
    auth_headers = [
        ("x-auth-key", apikey),
        ("x-auth-signature", sig),
        ("x-auth-timestamp", str(ts))]
    async with websockets.client.connect(uri, extra_headers=auth_headers) as websocket:
        await websocket.send("""{"op": "ping"}""")
        while True:
            msg = await websocket.recv()
            print(msg)

asyncio.get_event_loop().run_until_complete(
    websocket_auth_demo('wss://api-test.ascendex-sandbox.io:443/1/api/pro/v2/stream'))

