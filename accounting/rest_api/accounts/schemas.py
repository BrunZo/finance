"""Pydantic schemas for accounts API."""

from pydantic import BaseModel, ConfigDict, Field

from accounting.models import AccountType


class AccountUpsert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_type: str
    tag: str = Field(..., min_length=1)

    def to_account_type(self) -> AccountType:
        return AccountType(self.account_type)


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    account_type: AccountType
    tag: str

