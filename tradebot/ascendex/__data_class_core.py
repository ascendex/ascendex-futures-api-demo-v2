from dataclasses import dataclass, field, InitVar
from decimal import Decimal
from typing import List
from .__enums import *



@dataclass
class Auth:
    accountGroup: int
    email: str
    expireTime: int
    allowedIps: List[str]
    cashAccount: List[str]
    marginAccount: List[str]
    futuresAccount: List[str]
    userUID: str
    tradePermission: bool
    transferPermission: bool
    viewPermission: bool
    limitQuota: int


class PriceLevel:
    def __init__(self, price, size):
        self.price = Decimal(price)
        self.size = Decimal(size)
    @property
    def is_valid(self):
        return self.size > Decimal(0)

@dataclass
class BboData:
    ts: int
    bid: PriceLevel = None
    ask: PriceLevel = None

    def __post_init__(self):
        self.bid = PriceLevel(*self.bid)
        self.ask = PriceLevel(*self.ask)

@dataclass
class Bbo: # TODO: this data should be fixed.
    m: str
    symbol: str 
    data: BboData = None

    def __post_init__(self):
        self.data = BboData(**self.data)

    @property
    def bid(self):
        return self.data.bid
    
    @property
    def ask(self):
        return self.data.ask

@dataclass
class RefPrice:
    asset: str = None
    settlementAsset: str = None
    time: int = None
    price: Decimal = None

    a: InitVar[str] = None
    q: InitVar[str] = None
    t: InitVar[int] = None
    p: InitVar[str] = None

    def __post_init__(self, a, q, t, p):
        self.asset = self.asset or a
        self.settlementAsset = self.settlementAsset or q
        self.time = self.time or t
        self.price = Decimal(self.price or p)

@dataclass
class PriceFilter:
    maxPrice: Decimal
    minPrice: Decimal
    tickSize: Decimal

    def __post_init__(self):
        self.maxPrice = Decimal(self.maxPrice)
        self.minPrice = Decimal(self.minPrice)
        self.tickSize = Decimal(self.tickSize)

@dataclass
class LotSizeFilter:
    maxQty: Decimal
    minQty: Decimal
    lotSize: Decimal

    def __post_init__(self):
        self.maxQty = Decimal(self.maxQty)
        self.minQty = Decimal(self.minQty)
        self.lotSize = Decimal(self.lotSize)

@dataclass
class MarginRequirement:
    positionNotionalLowerBound: Decimal
    positionNotionalUpperBound: Decimal
    initialMarginRate: Decimal
    maintenanceMarginRate: Decimal

    def __post_init__(self):
        self.positionNotionalLowerBound = Decimal(self.positionNotionalLowerBound)
        self.positionNotionalUpperBound = Decimal(self.positionNotionalUpperBound)
        self.initialMarginRate = Decimal(self.initialMarginRate)
        self.maintenanceMarginRate = Decimal(self.maintenanceMarginRate)

@dataclass
class FuturesContractInfo:
    symbol: str
    displayName: str
    status: str
    settlementAsset: str
    underlying: str
    priceFilter: PriceFilter
    lotSizeFilter: LotSizeFilter
    commissionReserveRate: Decimal
    commissionType: CommissionType
    marketOrderPriceMarkup: Decimal
    marginRequirements: List[MarginRequirement] = field(default_factory=list)

    tradingStartTime: InitVar[int] = None
    collapseDecimals: InitVar[str] = None

    def __post_init__(self, tradingStartTime, collapseDecimals):
        self.priceFilter = PriceFilter(**self.priceFilter)
        self.lotSizeFilter = LotSizeFilter(**self.lotSizeFilter)
        marginRequirements = list(MarginRequirement(**x) for x in self.marginRequirements)
        self.marginRequirements = sorted(marginRequirements, key = lambda x: x.positionNotionalUpperBound)
        self.commissionReserveRate = Decimal(self.commissionReserveRate)
        self.commissionType = CommissionType._member_map_[self.commissionType.lower()]
        self.marketOrderPriceMarkup = Decimal(self.marketOrderPriceMarkup)

@dataclass
class FuturesPricingData:
    """Pricing Data for a Futures Contract"""
    symbol: str = None
    time: int = None
    nextFundingTime: int = None
    fundingRate: Decimal = None
    indexPrice: Decimal = None
    markPrice: Decimal = None

    s: InitVar[str] = None
    t: InitVar[int] = None
    f: InitVar[int] = None
    mp: InitVar[str] = None
    ip: InitVar[str] = None
    r: InitVar[str] = None

    def __post_init__(self, s, t, f, mp, ip, r):
        self.symbol = self.symbol or s
        self.time = self.time or t
        self.nextFundingTime = self.nextFundingTime or f
        self.fundingRate = Decimal(self.fundingRate or r)
        self.indexPrice = Decimal(self.indexPrice or ip)
        self.markPrice = Decimal(self.markPrice or mp)


@dataclass
class FuturesCollateralBalance:
    asset: str = None
    balance: Decimal = None
    discountFactor: Decimal = None
    
    a: InitVar[str] = None
    b: InitVar[str] = None
    f: InitVar[str] = None
    referencePrice: InitVar[Decimal] = None

    def __post_init__(self, a, b, f, referencePrice):
        self.asset = self.asset or a
        self.balance = Decimal(self.balance or b)
        self.discountFactor = Decimal(self.discountFactor or f)

@dataclass
class FuturesContractPosition:
    symbol: str = None
    marginType: MarginType = None
    side: str = None
    position: Decimal = None
    referenceCost: Decimal = None
    avgOpenPrice: Decimal = None
    isolatedMargin: Decimal = None
    leverage: Decimal = None
    realizedPnl: Decimal = None
    stopLossPrice: Decimal = None
    stopLossTrigger: str = None
    takeProfitPrice: Decimal = None
    takeProfitTrigger: str = None
    unrealizedPnl: Decimal = None
    buyOpenOrderNotional: Decimal = None
    sellOpenOrderNotional: Decimal = None

    markPrice: InitVar[Decimal] = None
    indexPrice: InitVar[Decimal] = None

    s: InitVar[str] = None
    mt: InitVar[str] = None
    sd: InitVar[str] = None
    pos: InitVar[str] = None
    rc: InitVar[str] = None
    aop: InitVar[str] = None
    up: InitVar[str] = None
    rp: InitVar[str] = None
    lev: InitVar[str] = None
    iw: InitVar[str] = None
    tp: InitVar[str] = None
    tpt: InitVar[str] = None
    sl: InitVar[str] = None
    slt: InitVar[str] = None
    boon: InitVar[str] = None
    soon: InitVar[str] = None

    def __post_init__(self, indexPrice, markPrices, s, mt, sd, pos, rc, aop, up, rp, lev, iw, tp, tpt, sl, slt, boon, soon):
        self.symbol = self.symbol or s
        self.marginType = MarginType._member_map_[self.marginType or mt]
        self.side = self.side or sd
        self.position = Decimal(self.position or pos)
        self.referenceCost = Decimal(self.referenceCost or rc)
        self.avgOpenPrice = Decimal(self.avgOpenPrice or aop)
        self.isolatedMargin = Decimal(self.isolatedMargin or iw)
        self.leverage = Decimal(self.leverage or lev)
        self.realizedPnl = Decimal(self.realizedPnl or rp)
        self.stopLossTrigger = self.stopLossTrigger or slt
        self.takeProfitTrigger = self.takeProfitTrigger or tpt
        self.stopLossPrice = Decimal(self.stopLossPrice or sl)
        self.takeProfitPrice = Decimal(self.takeProfitPrice or tp)
        self.unrealizedPnl = Decimal(self.unrealizedPnl or up)
        self.buyOpenOrderNotional = Decimal(self.buyOpenOrderNotional or boon)
        self.sellOpenOrderNotional = Decimal(self.sellOpenOrderNotional or soon)

@dataclass
class FuturesAccountPosition:
    time: int = None
    accountCategory: str = None
    accountId: str = None
    event: str = None
    collaterals: List[FuturesCollateralBalance] = field(default_factory=list)
    contracts: List[FuturesContractPosition] = field(default_factory=list)

    execId: int = -1

    at: InitVar[str] = None
    acc: InitVar[str] = None
    e: InitVar[str] = None
    t: InitVar[int] = -1
    m: InitVar[str] = None
    id: InitVar[str] = None
    sn: int = -1

    col: InitVar[List[FuturesCollateralBalance]] = None
    pos: InitVar[List[FuturesContractPosition]] = None


    def __post_init__(self, at, acc, e, t, m, id, col, pos):
        self.time = self.time or t
        self.accountId = self.accountId or acc
        self.accountCategory = self.accountCategory or at
        self.event = self.event or e

        collaterals = self.collaterals if len(self.collaterals) > 0 else col
        self.collaterals = list(FuturesCollateralBalance(**x) for x in collaterals)

        contracts = self.contracts if len(self.contracts) > 0 else pos
        self.contracts = list(FuturesContractPosition(**x) for x in contracts)
