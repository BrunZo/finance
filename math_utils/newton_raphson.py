from typing import Callable

def bisect(
    f: Callable[[float], float],
    a: float,
    b: float,
    eps: float
):
    assert f(a) * f(b) < 0

    while b - a > eps:
        m = a + (b - a) / 2
        if f(a) * f(m) < 0:
            b = m
        elif f(m) * f(b) < 0:
            a = m

    return a + (b - a) / 2

def newton_raphson(
    f: Callable[[float], float],
    x0: float
):
   pass 
