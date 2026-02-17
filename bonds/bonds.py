from dataclasses import dataclass

from investing.asset import Asset
from cf.cash_flow import Point
from rates.compound import continous_discount, yearly_discount
from rates.time import Time

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
                Time(k / self.m), 
                self.coupon_rate / self.m * self.face_value
            ) for k in range(self.periods)
        ]
        cash_flow[-1].value += self.face_value
        super().__init__(cash_flow, name)


if __name__ == "__main__":
    example_bond = Bond(0.01, 100, 20, 2, "Example Bond")
    print(example_bond.present_value(yearly_discount, y=0.04))
    print(example_bond.present_value(continous_discount, y=0.04))
