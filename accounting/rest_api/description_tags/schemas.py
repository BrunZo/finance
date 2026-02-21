"""Pydantic schemas for description -> account mapping API."""

from pydantic import BaseModel, ConfigDict

from accounting.models import DescriptionAccountMapping


class DescriptionAccountMappingOut(BaseModel):
    id: int
    description: str
    account_id: int
    account_name: str

    @classmethod
    def from_model(cls, model: DescriptionAccountMapping):
        return cls(
            id=model.id,
            description=model.description,
            account_id=model.account_id,
            account_name=model.account.name,
        )


class DescriptionAccountMappingUpsert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str
    account_id: int
