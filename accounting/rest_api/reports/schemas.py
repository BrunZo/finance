"""Pydantic schemas for reports API."""

from pydantic import BaseModel, ConfigDict


class ExpenseRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_name: str
    currency: str
    amount: float


class ExpenseTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    full_name: str
    direct_amounts_by_currency: dict[str, float]
    total_amounts_by_currency: dict[str, float]
    children: list["ExpenseTreeNode"]


ExpenseTreeNode.model_rebuild()


class ExpenseTreeResponse(BaseModel):
    children: list[ExpenseTreeNode]


class BalanceByCurrencyRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    account_name: str
    currency: str
    balance: float
