from dataclasses import dataclass
from typing import List

from investing.asset import Asset
from rates.discount_context import DiscountContext


@dataclass
class Portfolio:
    assets: List[Asset]

    def __init__(self, assets: List[Asset]):
        self.assets = assets

    def present_value(self, policy: DiscountContext) -> float:
        return sum(asset.present_value(policy) for asset in self.assets)

    def duration(self, policy: DiscountContext) -> float:
        return sum(asset.duration(policy) for asset in self.assets)

    def modified_duration(self, policy: DiscountContext) -> float:
        return sum(asset.modified_duration(policy) for asset in self.assets)

    def convexity(self, policy: DiscountContext) -> float:
        return sum(asset.convexity(policy) for asset in self.assets)

    def __str__(self) -> str:
        s = ""
        for asset in self.assets:
            s += f"  {asset.name} (length: {asset.length()})\n"
        return s
