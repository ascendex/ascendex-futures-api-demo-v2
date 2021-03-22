from enum import Enum

class MarginType(Enum):
    crossed = 0
    isolated = 1

class OrderSide(Enum):
    buy = 0
    sell = 1

class OrderType(Enum):
    limit = 0
    market = 1

class CommissionType(Enum):
    quote = 0
    base = 1
    received = 2
