from dataclasses import dataclass
from typing import List

from investing.asset import Asset
from rates.time import Time


@dataclass
class Portfolio:
    assets: List[Asset]

    def __init__(self, assets: List[Asset]):
        self.assets = assets

    def present_value(self, discount, now = Time(), **kwargs) -> float:
        return sum(asset.present_value(discount, now, **kwargs) for asset in self.assets)

    def duration(self, discount, now = Time(), **kwargs) -> float:
        return sum(asset.duration(discount, now, **kwargs) for asset in self.assets)

    def modified_duration(self, discount, now = Time(), **kwargs) -> float:
        return sum(asset.modified_duration(discount, now, **kwargs) for asset in self.assets)

    def convexity(self, discount, now = Time(), **kwargs) -> float:
        return sum(asset.convexity(discount, now, **kwargs) for asset in self.assets)

    def __str__(self) -> str:
        s = ""
        for asset in self.assets:
            s += f"  {asset.name} (length: {asset.length()})\n"
        return s
