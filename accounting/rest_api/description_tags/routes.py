"""API for mapping transaction descriptions to accounts (exact match, any account type)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from accounting.rest_api.deps import get_db
from accounting.rest_api.helpers import try_run
from accounting.rest_api.description_tags import schemas, services

router = APIRouter(prefix="/description-tags", tags=["description-tags"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("", response_model=schemas.DescriptionAccountMappingOut)
def insert_mapping(
    req: schemas.DescriptionAccountMappingUpsert,
    session: SessionDep,
) -> schemas.DescriptionAccountMappingOut:
    m = try_run(services.insert_mapping, session, req.description, req.account_id)
    return schemas.DescriptionAccountMappingOut.from_model(m)


@router.get("", response_model=list[schemas.DescriptionAccountMappingOut])
def list_mappings(session: SessionDep) -> list[schemas.DescriptionAccountMappingOut]:
    rows = services.list_mappings(session)
    return [
        schemas.DescriptionAccountMappingOut.from_model(m)
        for m in rows
    ]


@router.patch("/{mapping_id}", response_model=schemas.DescriptionAccountMappingOut)
def update_mapping(
    mapping_id: int,
    req: schemas.DescriptionAccountMappingUpsert,
    session: SessionDep,
) -> schemas.DescriptionAccountMappingOut:
    m = try_run(services.update_mapping_by_id, session, mapping_id, req.account_id)
    return schemas.DescriptionAccountMappingOut.from_model(m)


@router.delete("/{mapping_id}")
def delete_mapping(mapping_id: int, session: SessionDep) -> dict:
    deleted = services.delete_mapping(session, mapping_id)
    if not deleted:
        raise HTTPException(404, detail="Mapping not found")
    return {"ok": True}
