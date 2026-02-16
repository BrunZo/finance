"""Pydantic schemas for description -> expense account mapping API."""

from pydantic import BaseModel, ConfigDict

from accounting.models import DescriptionExpenseMapping


class DescriptionExpenseMappingOut(BaseModel):
    id: int
    description: str
    expense_account_id: int
    expense_account_name: str

    @classmethod
    def from_model(cls, model: DescriptionExpenseMapping):
        return cls(
            id=model.id,
            description=model.description,
            expense_account_id=model.expense_account_id,            
            expense_account_name=model.expense_account.name,
        )


class DescriptionExpenseMappingUpsert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str
    expense_account_id: int
