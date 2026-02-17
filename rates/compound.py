import math

from rates.time import Time

def yearly_discount(time: Time, now: Time, y: float = 0.0) -> float:
    return 1 / (1 + y) ** (time.time - now.time)

def continous_discount(time: Time, now: Time, y: float = 0.0) -> float:
    return math.exp(-y * (time.time - now.time))