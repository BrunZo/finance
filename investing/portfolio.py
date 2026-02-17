from dataclasses import dataclass
from typing import List

from investing.asset import Asset


@dataclass
class Portfolio:
    assets: List[Asset]

    def __init__(self, assets: List[Asset]):
        self.assets = assets

    def present_value(self, y: float) -> float:
        return sum(asset.present_value(y) for asset in self.assets)

    def duration(self, y: float) -> float:
        return sum(asset.duration(y) for asset in self.assets)

    def modified_duration(self, y: float) -> float:
        return sum(asset.modified_duration(y) for asset in self.assets)

    def convexity(self, y: float) -> float:
        return sum(asset.convexity(y) for asset in self.assets)

    def __str__(self) -> str:
        s = ""
        for asset in self.assets:
            s += f"  {asset.name} (length: {asset.length()})\n"
        return s
