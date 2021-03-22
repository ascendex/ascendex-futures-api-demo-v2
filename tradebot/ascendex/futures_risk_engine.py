import logging
from typing import Set
import random

from .__data_class_core import *
from .__data_class_user_defined import *
from .__enums import *
from .__util import *
from .ascendex_api import *


class FuturesRiskEngine(object):

    def __init__(self, host, apikey: str = None, secret: str = None):
        self.api = AscendExApi(host=host, apikey=apikey, secret=secret)

        self.error = ""

        self.futures_contract_info_by_symbol = None
        self.pricing_data_by_symbol = {}
        self.bbo_by_symbol = {}
        self.ref_price_by_asset = {}

        self.account_position: FuturesAccountPosition = None
        self.open_orders = None

        if apikey is not None and secret is not None:
            # self.api.authenticate()
            pass

    def initialize(self):
        self.refresh_futures_contract_info()
        return self

    @property
    def auth(self):
        if self.api.authenticated:
            return self.api.auth_data
        else:
            return self.__throw("You haven't authenticated the api engine yet")

    def refresh_futures_contract_info(self):
        map = self.api.get_futures_contract_info_by_symbol()
        if map == None:
            logging.warning("refresh_futures_contract_info failed")
        else:
            self.futures_contract_info_by_symbol = map

    def add_bbo(self, d: Bbo):
        logging.debug("calling add_bbo for %s" % d.symbol)
        self.bbo_by_symbol[d.symbol] = d
        return self

    def add_pricing_data(self, d: FuturesPricingData):
        logging.debug("calling add_pricing_data for %s" % d.symbol)
        self.pricing_data_by_symbol[d.symbol] = d
        return self

    def get_pricing_data(self, symbol: str) -> FuturesPricingData:
        return self.pricing_data_by_symbol.get(symbol)

    def add_ref_price(self, p: RefPrice):
        logging.debug("calling add_ref_price for %s" % p.asset)
        self.ref_price_by_asset[p.asset] = p
        return self

    def update_account_position(self, pos: FuturesAccountPosition):
        logging.info("calling update_account_position")
        self.account_position = pos
        return self

    def validate(func) :
        def wrapper(self, *args, **kwargs):
            if self.account_position is None:
                return self.__throw("object not initialized: account_position")
            elif self.futures_contract_info_by_symbol is None:
                return self.__throw("object not initialized: futures_contract_info_by_symbol")
            else:
                return func(self, *args, **kwargs)
        return wrapper

    def __throw(self, m) -> None:
        self.error = m
        return None

    @property
    @validate
    def total_margin(self):
        m = 0
        for a in self.account_position.collaterals:
            p: RefPrice = self.ref_price_by_asset.get(a.asset)
            if p is None: return self.__throw("missing reference price for " + a.asset)
            m = m + a.balance * a.discountFactor * p.price
        return m

    @property
    @validate
    def unrealized_pnl(self):
        return sum([x.unrealizedPnl for x in self.account_position.contracts])

    @property
    @validate
    def contract_position_notional(self):
        """Contract Position Notional (CPN) = sum(Contract Position * Mark Price)"""
        contracts = self.account_position.contracts
        crossed = Decimal(0)
        isolated = {}
        for c in contracts:
            if c.position.is_zero(): continue

            prc: FuturesPricingData = self.pricing_data_by_symbol.get(c.symbol)
            if prc is None: return self.__throw("missing pricing data for %s" % c.symbol)

            if c.marginType == MarginType.crossed:
                crossed = crossed + abs(c.position * prc.markPrice)
            elif c.marginType == MarginType.isolated:
                isolated[c.symbol] = abs(c.position * prc.markPrice)
            else:
                return self.__throw("unknown marginType: " + c.marginType)
        return ContractPositionNotional(crossed=crossed, isolated=isolated)

    @property
    @validate
    def position_margin(self):
        contracts = self.account_position.contracts
        cross_acc = MarginItem()
        isolated = {}

        for c in contracts:
            if c.position.is_zero(): continue

            prc: FuturesPricingData = self.pricing_data_by_symbol.get(c.symbol)
            if prc is None: return self.__throw("missing pricing data for %s" % c.symbol)

            info: FuturesContractInfo = self.futures_contract_info_by_symbol.get(c.symbol)
            if info is None: return self.__throw("missing FuturesContractInfo for %s" % c.symbol)

            position_notional = abs(c.position * prc.markPrice)
            margin_requirement = self.api.get_margin_requirement(position_notional, info)
            initial_margin = position_notional * margin_requirement.initialMarginRate
            maintenance_margin = position_notional * margin_requirement.maintenanceMarginRate


            if c.marginType == MarginType.crossed:
                cross_acc = cross_acc + \
                    MarginItem(
                        positionNotional=position_notional,
                        initialMargin=initial_margin,
                        maintanenceMargin=maintenance_margin,
                        unrealizedPnl=c.unrealizedPnl,
                    )
            elif c.marginType == MarginType.isolated:
                isolated[c.symbol] = \
                    IsolatedMarginData(
                        positionNotional=position_notional,
                        initialMargin=initial_margin,
                        maintanenceMargin=maintenance_margin,
                        unrealizedPnl=c.unrealizedPnl,
                        isolatedMargin=c.isolatedMargin,
                    )
            else:
                return self.__throw("unknown marginType: " + c.marginType)

        crossed_group_margin = self.total_margin - sum([m.isolatedMargin for m in isolated.values()])
        crossed = CrossedMarginData(
                    positionNotional=cross_acc.positionNotional,
                    initialMargin=cross_acc.initialMargin,
                    maintanenceMargin=cross_acc.maintanenceMargin,
                    unrealizedPnl=cross_acc.unrealizedPnl,
                    crossedGroupMargin=crossed_group_margin,
                )
        return PositionMargin(crossed=crossed, isolated=isolated)

    # Functions used for debugging

    @validate
    def place_random_order(self, symbol: str, side: OrderSide, id: str = "", is_maker: bool = True):
        info: FuturesContractInfo = self.futures_contract_info_by_symbol.get(symbol)
        bbo = self.bbo_by_symbol.get(symbol)
        if info is None:
            return self.__throw("contract info isn't available for " + symbol)
        elif bbo is None:
            return self.__throw("bbo not available for " + symbol)
        elif side == OrderSide.buy:
            if bbo.ask.price < Decimal(9999999):
                adj = (1 - random.random() * 0.1) if is_maker else (1 + random.random() * 0.1)
                prc = bbo.ask.price * Decimal(adj)
            else:
                prc = Decimal(21000)
        elif side == OrderSide.sell:
            if bbo.bid.price > Decimal(0):
                adj = (1 + random.random() * 0.1) if is_maker else (1 - random.random() * 0.1)
                prc = bbo.bid.price * Decimal(adj)
            else:
                prc = Decimal(19000)
        else:
            return self.__throw(f"Bbo price is invalid: bid={bbo.bid.price}, ask={bbo.ask.price}")
        round_up = False if side == OrderSide.buy else True
        prc = self.api.fix_price(prc, info.priceFilter, round_up=round_up)
        quantity = self.api.fix_size(Decimal(random.random() * 0.1), info.lotSizeFilter, round_up=True)
        resp = self.api.place_order(symbol, price=prc, quantity=quantity, side=side, id=id)
        return resp if resp is not None else self.__throw(self.api.error)

    def open_orders(self, symbol: str):
        """Fetch open order cached locally by the risk_engine"""
        return self.__throw("Not Implemented")
