"""Pydantic schemas for transactions API."""

from pydantic import BaseModel, Field


class SplitItem(BaseModel):
    account_id: int
    amount: str  # decimal string: positive=debit, negative=credit


class SplitsRequest(BaseModel):
    description: str = Field(..., min_length=1)
    splits: list[SplitItem] = Field(..., min_length=2)


class SplitOut(BaseModel):
    id: int
    account_id: int
    account_name: str
    amount: str


class SplitUpdate(BaseModel):
    account_id: int = Field(..., gt=0)


class TransactionOut(BaseModel):
    id: int
    timestamp: str
    description: str | None
    ext_ref: str | None = None
    splits: list[SplitOut]


class UncategorizedSplitOut(BaseModel):
    split_id: int
    transaction_id: int
    description: str
    amount: str
    account_id: int
    account_name: str
