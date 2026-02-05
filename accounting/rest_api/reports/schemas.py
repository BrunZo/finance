"""Pydantic schemas for reports API."""

from pydantic import BaseModel


class ExpenseRow(BaseModel):
    account_name: str
    amount: float
