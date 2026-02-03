from dataclasses import dataclass

from ..math.newton_raphson import bisect
from ..cf.cash_flow import CashFlow

@dataclass
class Bond:
    coupon_rate: float
    face_value: float
    periods: int
    m: int

    def cash_flow(self) -> CashFlow:
        cash_flow = [
            CashFlow.Point(k, self.coupon_rate / self.m * self.face_value) for k in range(self.periods)
        ]
        cash_flow[-1].value += self.face_value
        return CashFlow(cash_flow)

    def present_value(self, y: float) -> float:
        return self.cash_flow().present_value(y / self.m)

    def yield_from_price(self, p: float) -> float:
        return bisect(
            lambda y: self.present_value(y) - p,
            0, 1, 10 ** (-9)
        )

    def duration(self, y: float) -> float:
        return self.cash_flow().duration(y / self.m)

    def modified_duration(self, y: float) -> float:
        _duration = self.duration(y) / self.m
        factor = 1 / (1 + y / self.m)
        return factor * _duration

example_bond = Bond(0.01, 100, 20, 2)

print(example_bond.yield_from_price(90))
print(example_bond.modified_duration(0.05))
