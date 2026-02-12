"""Pydantic schemas for description -> expense account mapping API."""

from pydantic import BaseModel, Field


class DescriptionTagMappingOut(BaseModel):
    id: int
    description: str
    account_id: int
    account_name: str


class DescriptionTagMappingUpsert(BaseModel):
    description: str = Field(..., min_length=1)
    account_id: int = Field(..., gt=0)
