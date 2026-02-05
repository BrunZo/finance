"""Pydantic schemas for transactions API."""

from pydantic import BaseModel, Field


class SplitItem(BaseModel):
    account_id: int
    amount: str  # decimal string: positive=debit, negative=credit


class SplitsRequest(BaseModel):
    description: str = Field(..., min_length=1)
    splits: list[SplitItem] = Field(..., min_length=2)


class FriendAmount(BaseModel):
    friend_name: str = ""
    amount: str


class Expense(BaseModel):
    description: str = Field(..., min_length=1)
    source_account_id: int
    expense_account_id: int
    amount: str


class PayForManyRequest(BaseModel):
    description: str = Field(..., min_length=1)
    source_account_id: int
    expense_account_id: int
    total_amount: str
    my_share: str
    friend_amounts: list[FriendAmount] = Field(default_factory=list)


class BeingPaidForRequest(BaseModel):
    description: str = Field(..., min_length=1)
    liability_account_id: int
    expense_account_id: int
    my_expense_share: str
    receivable_total: str = "0"
    friend_amounts: list[FriendAmount] | None = None


class ReceiveReceivableRequest(BaseModel):
    description: str = Field(..., min_length=1)
    amount: str
    from_receivable_account_id: int
    to_bank_account_id: int


class PayPayableRequest(BaseModel):
    description: str = Field(..., min_length=1)
    amount: str
    payable_account_id: int
    from_bank_account_id: int

