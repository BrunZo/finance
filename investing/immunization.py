from typing import List

import numpy as np

from investing.asset import Asset
from investing.portfolio import Portfolio
from rates.time import Time
from typing import Callable, Any


def immunize(
    portfolio: Portfolio,
    available_assets: List[Asset],
    discount: Callable[[Time, Time, Any], float],
    now: Time = Time(),
    **kwargs,
):
    """
    Immunize the portfolio to the given yield rate.
    Naively implemented for integer solutions.
    """
    target_pv = -portfolio.present_value(discount, now, **kwargs)
    target_duration = portfolio.duration(discount, now, **kwargs)

    pvs = np.array([a.present_value(discount, now, **kwargs) for a in available_assets])
    durations = np.array([a.duration(discount, now, **kwargs) for a in available_assets])

    # System: sum(amount_i * pv_i) = target_pv
    #         sum(amount_i * pv_i * duration_i) = target_duration * target_pv
    A = np.vstack([pvs, pvs * durations])
    b = np.array([target_pv, target_duration * target_pv])

    amounts, *_ = np.linalg.lstsq(A, b, rcond=None)
    amounts = np.round(amounts)

    for asset, amount in zip(available_assets, amounts):
        for _ in range(int(amount)):
            portfolio.assets.append(asset)
