from dataclasses import dataclass, field
from typing import Any, Callable

from rates.time import Time


@dataclass
class DiscountContext:
    discount: Callable[[Time, Time, Any], float]
    now: Time = field(default_factory=Time)
    kwargs: dict = field(default_factory=dict)

    def __call__(self, time: Time) -> float:
        return self.discount(time, self.now, **self.kwargs)
