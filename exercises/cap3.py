import math
from typing import Callable

from bonds.bonds import Bond
from cf.cash_flow import CashFlow, Point
from math_utils.newton_raphson import bisect

# Exercise 1: Amortization
total_debt = 25000
periods = 7 * 12
interest_rate = .07
ans = 12 * bisect(
    lambda r: CashFlow([
        Point((i + 1) / 12, r) for i in range(periods)
    ]).present_value(interest_rate, nominal=True) - total_debt,
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
    return CashFlow([Point(a + 1, annual_payment) for a in range(age - current_age)]).present_value(interest_rate)

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
print(f"Duration = {bond.duration(0.1):.2f}")
