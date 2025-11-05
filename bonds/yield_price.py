from dataclasses import dataclass
import matplotlib.pyplot as plt
from typing import List

from math_utils.newton_raphson import bisect

@dataclass
class Bond:
    coupon_rate: float
    face_value: float
    periods: int
    m: int

def present_value(
    y: float,
    cash_flow: List[float]
):
    price = 0
    for k in range(len(cash_flow)):
        price += cash_flow[k] * 1 / (1 + y) ** (k + 1)
    return price

def duration(
    y: float,
    cash_flow: List[float]
):
    duration = 0
    for k in range(len(cash_flow)):
        duration += cash_flow[k] * 1 / (1 + y) ** (k + 1) * k
    duration /= present_value(y, cash_flow)
    return duration

def bond_cash_flow(
    bond: Bond
):
    cash_flow = []
    for _ in range(bond.periods):
        payment = bond.coupon_rate / bond.m * bond.face_value
        cash_flow.append(payment)
    cash_flow[-1] += bond.face_value
    return cash_flow


def price_from_yield(
    y: float,
    bond: Bond
):
    cash_flow = bond_cash_flow(bond)
    return present_value(y / bond.m, cash_flow)

def yield_from_price(
    p: float,
    bond: Bond
):
    return bisect(
        lambda y: price_from_yield(y, bond) - p,
        0, 1, 10 ** (-9)
    ) 

def modified_duration(
    y: float,
    bond: Bond
):
    cash_flow = bond_cash_flow(bond)
    _duration = duration(y, cash_flow) / bond.m
    factor = 1 / (1 + y / bond.m)  
    return factor * _duration

example_bond = Bond(0.01, 100, 20, 2)

print(modified_duration(0.05, example_bond))
