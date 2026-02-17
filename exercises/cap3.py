import math
from typing import Callable

from bonds.bonds import Bond
from cf.cash_flow import CashFlow, Point
from investing.asset import Asset
from investing.immunization import immunize
from investing.portfolio import Portfolio
from math_utils.newton_raphson import bisect
from rates.compound import yearly_discount
from rates.time import Time

# Exercise 1: Amortization
total_debt = 25000
periods = 7 * 12
interest_rate = .07
ans = 12 * bisect(
    lambda r: CashFlow([
        Point(Time((i + 1) / 12), r) for i in range(periods)
    ]).present_value(yearly_discount, y=interest_rate) - total_debt,
    0, 100000, 10 ** (-9)
)
print(f"Monthly payments = $ {ans:.4f}")

# Exercise 3: Uncertain annuity
current_age = 90
ages = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101]
probs = [.07, .08, .09, .10, .10, .10, .10, .10, .10, .07, .05, .04]
life_expectancy = sum(
    age * prob for age, prob in zip(ages, probs)
)
print(f"Life expectancy = {life_expectancy:.2f} years")

annual_payment = 10000
interest_rate = .08

def present_value_till_age(age: int) -> CashFlow:
    cf = CashFlow([Point(Time(a + 1), annual_payment) for a in range(current_age, age)])
    return cf.present_value(yearly_discount, now=Time(current_age), y=interest_rate)

def int_average(t: float, fn: Callable[int, float]) -> float:
    if t == math.floor(t):
        return fn(t)
    return (
        fn(math.floor(t)) * (math.ceil(t) - t) +
        fn(math.ceil(t)) * (t - math.floor(t))
    )

expected_present_value = int_average(life_expectancy, present_value_till_age)
print(f"Expected present value = $ {expected_present_value:.2f}")

expected_present_value = sum(
    present_value_till_age(age) * prob
    for age, prob in zip(ages, probs)
)
print(f"Expected present value = $ {expected_present_value:.2f}")

# Exercise 9
bond = Bond(0.08, 100, 10, 1, "10y 8% Bond")
print(f"Duration = {bond.duration(yearly_discount, y=0.1):.2f}")

# Exercise 12
bond_A = Asset([
    Point(Time(1), 100),
    Point(Time(2), 100),
    Point(Time(3), 100 + 1000),
], "Bond A")
bond_B = Asset([
    Point(Time(1), 50),
    Point(Time(2), 50),
    Point(Time(3), 50 + 1000),
], "Bond B")
bond_C = Asset([
    Point(Time(1), 0),
    Point(Time(2), 0),
    Point(Time(3), 0 + 1000),
], "Bond C")
bond_D = Asset([Point(Time(1), 1000)], "Bond D")
all_bonds = [bond_A, bond_B, bond_C, bond_D]
yield_rate = 0.15
for bond in all_bonds:
    print(f"Bond {bond.name}")
    print(f"   price = {bond.present_value(yearly_discount, y=yield_rate):.2f}")
    print(f"   duration = {bond.duration(yearly_discount, y=yield_rate):.2f}")

portfolio = Portfolio([
    Asset([Point(Time(2), -20000)], "Payment Obligation")
])
immunize(portfolio, all_bonds, yearly_discount, now=Time(2), y=yield_rate)
print(f"Immunized portfolio: {portfolio}")