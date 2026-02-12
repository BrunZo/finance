"""Pydantic schemas for transactions API."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class SplitItem(BaseModel):
    account_id: int
    amount: Decimal


class SplitsRequest(BaseModel):
    description: str = Field(..., min_length=1)
    splits: list[SplitItem] = Field(..., min_length=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class SplitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    amount: Decimal


class SplitUpdate(BaseModel):
    account_id: int = Field(..., gt=0)


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    description: str | None
    external_reference: str | None = None
    currency: str | None = None
    splits: list[SplitOut]

