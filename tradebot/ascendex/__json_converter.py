import logging
from datetime import datetime

from .__data_class_core import *
from .__data_class_user_defined import *


def _long2ts(t: int) -> str:
    return datetime.fromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S')


def float2json(v, name, err):
    if v is None:
        return {"error": err}
    else:
        return {name: float(v)}


class JsonConverter(object):

    def __init__(self, obj, error: str = ""):
        self.__obj = obj
        self.__error = error

    def to_json(self):
        logging.debug("calling to_json with object type = %s" % str(type(self.__obj)))
        o = self.__obj
        if o is None: return self.__do_error()
        elif isinstance(o, dict): return o
        elif isinstance(o, Auth): return self.__do_Auth()
        elif isinstance(o, PriceLevel): return self.__do_PriceLevel()
        elif isinstance(o, BboData): return self.__do_BboData()
        elif isinstance(o, Bbo): return self.__do_Bbo()
        elif isinstance(o, RefPrice): return self.__do_RefPrice()
        elif isinstance(o, PriceFilter): return self.__do_PriceFilter()
        elif isinstance(o, LotSizeFilter): return self.__do_LotSizeFilter()
        elif isinstance(o, MarginRequirement): return self.__do_MarginRequirement()
        elif isinstance(o, FuturesContractInfo): return self.__do_FuturesContractInf()
        elif isinstance(o, FuturesPricingData): return self.__do_FuturesPricingData()
        elif isinstance(o, FuturesCollateralBalance): return self.__do_FuturesCollateralBalance()
        elif isinstance(o, FuturesContractPosition): return self.__do_FuturesContractPosition()
        elif isinstance(o, FuturesAccountPosition): return self.__do_FuturesAccountPosition()
        # user defined
        elif isinstance(o, ContractPositionNotional): return self.__do_ContractPositionNotional()
        elif isinstance(o, CrossedMarginData): return self.__do_CrossedMarginData()
        elif isinstance(o, IsolatedMarginData): return self.__do_IsolatedMarginData()
        elif isinstance(o, PositionMargin): return self.__do_PositionMargin()
        else: return { "error": "invalid object type" + str(type(o)) }

    def __do_error(self):
        return dict(error = self.__error)

    def __do_Auth(self):
        o: Auth = self.__obj
        return dict(
            accountGroup = o.accountGroup,
            email = o.email,
            expireTime = o.expireTime,
            allowedIps = o.allowedIps,
            cashAccount = o.cashAccount,
            marginAccount = o.marginAccount,
            futuresAccount = o.futuresAccount,
            userUID = o.userUID,
            tradePermission = o.tradePermission,
            transferPermission = o.transferPermission,
            viewPermission = o.viewPermission,
            limitQuota = o.limitQuota,
        )

    def __do_PriceLevel(self):
        o = self.__obj
        return dict(
            price = float(o.price),
            size = float(o.size),
        )

    def __do_BboData(self):
        o = self.__obj
        return dict(
            ts = o.ts,
            bid = JsonConverter(o.bid).to_json(),
            ask = JsonConverter(o.ask).to_json(),
        )

    def __do_Bbo(self):
        o = self.__obj
        return dict(
            m = o.m,
            symbol = o.symbol,
            data = JsonConverter(o.data).to_json()
        )

    def __do_RefPrice(self):
        o = self.__obj
        return dict(
            asset=o.asset,
            quoteAsset=o.quoteAsset,
            time=_long2ts(o.time),
            price=float(o.price),
        )

    def __do_PriceFilter(self):
        o = self.__obj
        return dict(
            maxPrice = float(o.maxPrice),
            minPrice = float(o.minPrice),
            tickSize = float(o.tickSize),
        )

    def __do_LotSizeFilter(self):
        o = self.__obj
        return dict(
            maxQty = float(o.maxQty),
            minQty = float(o.minQty),
            lotSize = float(o.lotSize),
        )

    def __do_MarginRequirement(self):
        o = self.__obj
        return dict(
            positionLB = float(o.positionLB),
            positionUB = float(o.positionUB),
            initialMarginRate = float(o.initialMarginRate),
            maintenanceMarginRate = float(o.maintenanceMarginRate),
        )

    def __do_FuturesContractInfo(self):
        o = self.__obj
        return dict(
            symbol = o.symbol,
            displayName = o.displayName,
            status = o.status,
            quoteAsset = o.quoteAsset,
            baseAsset = o.baseAsset,
            underlying = o.underlying,
            priceFilter = JsonConverter(o.priceFilter).to_json(),
            lotSizeFilter = JsonConverter(o.lotSizeFilter).to_json(),
            marginRequirements = [JsonConverter(x).to_json() for x in o.marginRequirements],
        )

    def __do_FuturesPricingData(self):
        o = self.__obj
        return dict(
            symbol=o.symbol,
            time=_long2ts(o.time),
            nextFundingTime=_long2ts(o.nextFundingTime),
            fundingRate=float(o.fundingRate),
            indexPrice=float(o.indexPrice),
            markPrice=float(o.markPrice),
        )

    def __do_FuturesCollateralBalance(self):
        o = self.__obj
        return dict(
            asset=o.asset,
            balance=float(o.balance),
            discountFactor=float(o.discountFactor),
        )

    def __do_FuturesContractPosition(self):
        o: FuturesContractPosition = self.__obj
        return dict(
            symbol=o.symbol,
            marginType=o.marginType.name,
            side=o.side,
            position=float(o.position),
            referenceCost=float(o.referenceCost),
            avgOpenPrice=float(o.avgOpenPrice),
            isolatedMargin=float(o.isolatedMargin),
            leverage=float(o.leverage),
            realizedPnl=float(o.realizedPnl),
            stopLossPrice=float(o.stopLossPrice),
            stopLossTrigger=o.stopLossTrigger,
            takeProfitPrice=float(o.takeProfitPrice),
            takeProfitTrigger=o.takeProfitTrigger,
            unrealizedPnl=float(o.unrealizedPnl),
            buyOpenOrderNotional=float(o.buyOpenOrderNotional),
            sellOpenOrderNotional=float(o.sellOpenOrderNotional),
        )

    def __do_FuturesAccountPosition(self):
        o = self.__obj
        return dict(
            time=_long2ts(o.time),
            accountCategory=o.accountCategory,
            accountId=o.accountId,
            event=o.event,
            collaterals=[JsonConverter(x).to_json() for x in o.collaterals],
            contracts=[JsonConverter(x).to_json() for x in o.contracts],
        )

    # User Defined
    def __do_ContractPositionNotional(self):
        o: ContractPositionNotional = self.__obj
        return dict(
            crossed=float(o.crossed),
            isolated={ k: float(v) for k,v in o.isolated }
        )

    def __do_CrossedMarginData(self):
        o: CrossedMarginData = self.__obj
        return dict(
            positionNotional=float(o.positionNotional),
            initialMargin=float(o.initialMargin),
            maintanenceMargin=float(o.maintanenceMargin),
            unrealizedPnl=float(o.unrealizedPnl),
            crossedGroupMargin=float(o.crossedGroupMargin),
            maintanenceMarginRatio=float(o.maintanenceMarginRatio),
        )

    def __do_IsolatedMarginData(self):
        o: IsolatedMarginData = self.__obj
        return dict(
            positionNotional=float(o.positionNotional),
            initialMargin=float(o.initialMargin),
            maintanenceMargin=float(o.maintanenceMargin),
            unrealizedPnl=float(o.unrealizedPnl),
            isolatedMargin=float(o.isolatedMargin),
            maintanenceMarginRatio=float(o.maintanenceMarginRatio),
        )

    def __do_PositionMargin(self):
        o: PositionMargin = self.__obj
        return dict(
            crossed=JsonConverter(o.crossed).to_json(),
            isolated={ k: JsonConverter(v).to_json() for k, v in o.isolated.items() }
        )
