import logging
import requests
import uuid

from typing import Mapping
import math

from .__data_class_core import *
from .__util import *
from .__enums import *


def S(x: Decimal) -> str: return "{:.9f}".format(x)


class AscendExApi(object):

    def __init__(self, host, apikey, secret):
        self.__apikey = apikey
        self.__secret = secret
        self.__host = host
        self.__auth: Auth = None
        self.error = ""

    def make_auth_headers(self, path):
        ts = get_timestamp()
        return ts, make_auth_headers(ts, path, self.__apikey, self.__secret)

    def authenticate(self):
        #url = self.__host + "/info"
        logging.warning("overwrite host for authentication")
        url = self.__host + "/api/pro/v1/info"
        _, headers = self.make_auth_headers("info")
        res = requests.get(url, headers=headers)
        if res.status_code != 200 or res.json()['code'] != 0:
            raise Exception("Authentication failed:" + str(res.json()))
        self.__auth = Auth(**(res.json()['data']))

    @property
    def auth_data(self):
        return self.__auth

    @property
    def authenticated(self):
        return self.__auth is not None

    # Utilities
    def __throw(self, msg):
        self.error = msg

    # Decorator
    def private(func) :
        def wrapper(self, *args, **kwargs):
            if self.authenticated:
                return func(self, *args, **kwargs)
            else:
                return self.__throw("authentication needed for accessing private end points")
        return wrapper

    # APIs
    def get_futures_contract_info_by_symbol(self) -> Mapping[str, FuturesContractInfo]:
        url = self.__host + "/api/pro/v2/futures/contract"
        logging.info("calling get_futures_contract_info with url = %s" % url)
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()["data"]
            return { x['symbol']: FuturesContractInfo(**x) for x in data }

    @staticmethod
    def get_margin_requirement(position_notional: Decimal, contract_info: FuturesContractInfo) -> MarginRequirement:
        return next(x for x in contract_info.marginRequirements if x.positionUB > position_notional)

    @property
    @private
    def private_host(self):
        return f"{self.__host}/{self.__auth.accountGroup}/api/pro"

    @private
    def change_margin_type(self, symbol: str, margin_type: MarginType):
        api_path = "v2/futures/margin-type"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        args = dict(symbol = symbol, marginType = margin_type.name)
        logging.info(f"calling POST {url}(symbo={symbol}, margin_type={margin_type})")
        res = requests.post(url, headers=headers, json=args)
        if res.status_code != 200:
            return self.__throw(f"change_margin_type failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def change_ios_position_margin(self, symbol, amount):
        api_path = "v2/futures/isolated-position-margin"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        args = dict(symbol = symbol, amount = str(amount))
        logging.info(f"calling POST {url}(symbo={symbol}, amount={amount})")
        res = requests.post(url, headers=headers, json=args)
        if res.status_code != 200:
            return self.__throw(f"change_ios_position_margin failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def change_leverage(self, symbol: str, leverage: int):
        api_path = "v2/futures/leverage"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        params = dict(symbol=symbol, leverage=leverage)
        res = requests.post(url, headers=headers, params=params)
        if res.status_code != 200:
            return self.__throw(f"change_leverage failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def deposit_to_futures(self, asset: str, amount: str):
        api_path = "v2/futures/transfer/deposit"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        params = dict(asset=asset, amount=amount)
        res = requests.post(url, headers=headers, params=params)
        if res.status_code != 200:
            return self.__throw(f"deposit_to_futures failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def withdraw_from_futures(self, asset: str, amount: str):
        api_path = "v2/futures/transfer/withdraw"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        params = dict(asset=asset, amount=amount)
        res = requests.post(url, headers=headers, params=params)
        if res.status_code != 200:
            return self.__throw(f"withdraw_from_futures failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def free_margin(self):
        api_path = "v2/futures/free-margin"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return self.__throw(f"withdraw_from_futures failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def get_futures_position(self):
        api_path = "v2/futures/position"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return self.__throw(f"futures collateral failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def open_orders(self, symbol):
        api_path = "v2/futures/order/open"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        params = dict(symbol=symbol)
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            return self.__throw(f"oepn_orders failed with status code = {res.status_code}: {res.text}")
        return res.json()

    @private
    def place_order(self, symbol, price: Decimal, quantity: Decimal, side: OrderSide,
                    order_type: OrderType = OrderType.limit, id: str = ""):
        api_path = "v2/futures/order"
        url = self.private_host + "/" + api_path
        ts, headers = self.make_auth_headers(api_path)
        id = uuid.uuid4().hex if len(id) == 0 else id
        params = dict(id=id, time=ts, symbol=symbol, orderPrice=S(price),
                      orderQty=S(quantity), orderType=order_type.name, side=side.name)
        res = requests.post(url, headers=headers, json=params)
        if res.status_code != 200:
            return self.__throw(f"oepn_orders failed with status code = {res.status_code}: {res.text}")
        return res.json()

    def fix_price(self, price: Decimal, price_filter: PriceFilter, round_up: bool = True) -> Decimal:
        p = price / price_filter.tickSize
        p = (math.ceil(p) if round_up else math.floor(p)) * price_filter.tickSize
        return p.max(price_filter.minPrice).min(price_filter.maxPrice)

    def fix_size(self, size: Decimal, size_filter: LotSizeFilter, round_up: bool = True) -> Decimal:
        s = size / size_filter.lotSize
        s = (math.ceil(s) if round_up else math.floor(s)) * size_filter.lotSize
        return s.max(size_filter.minQty).min(size_filter.maxQty)

