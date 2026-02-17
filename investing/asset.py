from dataclasses import dataclass
from typing import List

from cf.cash_flow import CashFlow, Point


@dataclass
class Asset(CashFlow):
    name: str

    def __init__(self, cash_flow: List[Point], name: str):
        super().__init__(cash_flow)
        self.name = name
