from dataclasses import dataclass
from typing import Any, Callable, List

from math_utils.newton_raphson import bisect
from rates.time import Time


@dataclass
class Point:
    time: Time
    value: float

    def present_value(
        self, 
        discount: Callable[[Time, Time, Any], float],
        now: Time = Time(),
        **kwargs,
    ) -> float:
        return self.value * discount(self.time, now, **kwargs)


@dataclass
class CashFlow:
    cash_flow: List[Point]

    def __init__(self, cash_flow: List[Point]):
        self.cash_flow = cash_flow

    def length(self) -> int:
        return len(self.cash_flow)

    def present_value(self, discount, now = Time(), **kwargs) -> float:
        return sum(
            point.present_value(discount, now, **kwargs) 
            for point in self.cash_flow
        )
    
    def duration(self, discount, now = Time(), **kwargs) -> float:
        return sum(
            point.time.time * point.present_value(discount, now, **kwargs) 
            for point in self.cash_flow
        ) / self.present_value(discount, now, **kwargs)

    def modified_duration(self, discount, now = Time(), **kwargs) -> float:
        pass 
        # TODO

    def convexity(self, discount, now = Time(), **kwargs) -> float:
        pass
        # TODO
