from dataclasses import dataclass, field

from decimal import Decimal
from typing import Mapping


@dataclass
class ContractPositionNotional:
    crossed: Decimal
    isolated: Mapping[str, Decimal] = None

    def __post_init__(self):
        self.crossed = Decimal(self.crossed)
        self.isolated = {} if self.isolated is None else {k: Decimal(v) for k, v in self.isolated.items()}

@dataclass
class MarginItem:
    positionNotional: Decimal = field(default_factory=Decimal)
    initialMargin: Decimal = field(default_factory=Decimal)
    maintanenceMargin: Decimal = field(default_factory=Decimal)
    unrealizedPnl: Decimal = field(default_factory=Decimal)

    def __add__(self, other):
        return MarginItem(
            positionNotional=self.positionNotional + other.positionNotional,
            initialMargin=self.initialMargin + other.initialMargin,
            maintanenceMargin=self.maintanenceMargin + other.maintanenceMargin,
            unrealizedPnl=self.unrealizedPnl + other.unrealizedPnl,
        )

@dataclass
class CrossedMarginData:
    positionNotional: Decimal
    initialMargin: Decimal
    maintanenceMargin: Decimal
    unrealizedPnl: Decimal
    crossedGroupMargin: Decimal
    maintanenceMarginRatio: Decimal = field(default_factory=Decimal)

    def __post_init__(self):
        # TODO: how to handle special case
        group_value = self.unrealizedPnl + self.crossedGroupMargin
        self.maintanenceMarginRatio = Decimal(0) if group_value.is_zero() else self.maintanenceMargin / group_value

@dataclass
class IsolatedMarginData:
    positionNotional: Decimal
    initialMargin: Decimal
    maintanenceMargin: Decimal
    unrealizedPnl: Decimal
    isolatedMargin: Decimal
    maintanenceMarginRatio: Decimal = field(default_factory=Decimal)

    def __post_init__(self):
        # TODO: how to handle special case
        m = self.unrealizedPnl + self.isolatedMargin
        self.maintanenceMarginRatio = Decimal(0) if m.is_zero() else self.maintanenceMargin / m

@dataclass
class PositionMargin:
    crossed: CrossedMarginData
    isolated: Mapping[str, IsolatedMarginData]

