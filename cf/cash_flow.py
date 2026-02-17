from dataclasses import dataclass
from typing import List

from rates.discount_context import DiscountContext
from rates.time import Time


@dataclass
class Point:
    time: Time
    value: float

    def present_value(self, policy: DiscountContext) -> float:
        return self.value * policy(self.time)


@dataclass
class CashFlow:
    cash_flow: List[Point]

    def __init__(self, cash_flow: List[Point]):
        self.cash_flow = cash_flow

    def length(self) -> int:
        return len(self.cash_flow)

    def present_value(self, policy: DiscountContext) -> float:
        return sum(point.present_value(policy) for point in self.cash_flow)

    def duration(self, policy: DiscountContext) -> float:
        return sum(
            point.time.time * point.present_value(policy) for point in self.cash_flow
        ) / self.present_value(policy)

    def modified_duration(self, policy: DiscountContext) -> float:
        pass
        # TODO

    def convexity(self, policy: DiscountContext) -> float:
        pass
        # TODO
