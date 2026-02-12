"""Pydantic schemas for reports API."""

from pydantic import BaseModel, ConfigDict


class ExpenseRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_name: str
    amount: float
