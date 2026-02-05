"""Pydantic schemas for accounts API."""

from pydantic import BaseModel

from accounting.models import Account, AccountType


class AccountOut(BaseModel):
    id: int
    name: str
    account_type: str
    tag: str

    @classmethod
    def from_account(cls, account: Account) -> "AccountOut":
        return cls(
            id=account.id,
            name=account.name,
            account_type=account.account_type.value,
            tag=account.tag,
        )


class AccountCreate(BaseModel):
    account_type: str  # asset, liability, income, expense
    tag: str

    def to_account_type(self) -> AccountType:
        return AccountType(self.account_type)
