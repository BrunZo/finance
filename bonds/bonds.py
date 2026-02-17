from dataclasses import dataclass

from investing.asset import Asset
from math_utils.newton_raphson import bisect
from cf.cash_flow import Point, CashFlow

@dataclass
class Bond(Asset):
    coupon_rate: float
    face_value: float
    periods: int
    m: int

    def __init__(self, coupon_rate: float, face_value: float, periods: int, m: int, name: str):
        self.coupon_rate = coupon_rate
        self.face_value = face_value
        self.periods = periods
        self.m = m
        cash_flow = [
            Point(
                k / self.m, 
                self.coupon_rate / self.m * self.face_value
            ) for k in range(self.periods)
        ]
        cash_flow[-1].value += self.face_value
        super().__init__(cash_flow, name)


if __name__ == "__main__":
    example_bond = Bond(0.01, 100, 20, 2, "Example Bond")
    print(example_bond.yield_from_price(90))
    print(example_bond.modified_duration(0.05))
