from dataclasses import dataclass
from typing import List

@dataclass
class CashFlow:

    @dataclass
    class Point:
        time: float
        value: float

        def _discount(self, y: float) -> float:
            return 1 / (1 + y) ** self.time

        def present_value(self, y: float) -> float:
            return self.value * self._discount(y)

    cash_flow: List[Point]

    def __init__(self, cash_flow: List[Point]):
        self.cash_flow = cash_flow

    def present_value(self, y: float) -> float:
        return sum(point.present_value(y) for point in self.cash_flow)

    def duration(self, y: float) -> float:
        return sum(point.time * point.present_value(y) for point in self.cash_flow) / self.present_value(y)

