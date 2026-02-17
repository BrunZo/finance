import math
from dataclasses import dataclass
from typing import List

from math_utils.newton_raphson import bisect


@dataclass
class Point:
    time: float
    value: float

    def _discount(self, y: float, nominal=False) -> float:
        if not nominal:
            return 1 / (1 + y) ** self.time

        whole_years = math.floor(self.time)
        discount = 1 / (1 + y) ** whole_years
        
        remainder = self.time - whole_years
        if remainder != 0:
            discount *= 1 / (1 + y * remainder)
        
        return discount 

    def present_value(self, y: float, nominal=False) -> float:
        return self.value * self._discount(y, nominal=nominal)


@dataclass
class CashFlow:
    cash_flow: List[Point]

    def __init__(self, cash_flow: List[Point]):
        self.cash_flow = cash_flow

    def yield_from_price(self, p: float) -> float:
        return bisect(
            lambda r: self.present_value(r) - p,
            0, 1, 10 ** (-9)
        )

    def present_value(self, r: float, nominal=False) -> float:
        return sum(
            point.present_value(r, nominal=nominal) 
            for point in self.cash_flow
        )
    
    def duration(self, r: float) -> float:
        return sum(point.time * point.present_value(r) for point in self.cash_flow) / self.present_value(r)

    def modified_duration(self, r: float) -> float:
        return self.duration(r) / (1 + r)

    def convexity(self, r: float) -> float:
        return sum(
            point.time * (point.time + 1) * point.present_value(r) 
            for point in self.cash_flow
        ) / self.present_value(r) ** 2
