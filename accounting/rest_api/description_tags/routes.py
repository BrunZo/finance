"""API for mapping transaction descriptions to expense tags (exact match)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from accounting.rest_api.deps import get_db
from accounting.rest_api.description_tags import schemas, services

router = APIRouter(prefix="/description-tags", tags=["description-tags"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[schemas.DescriptionTagMappingOut])
def list_mappings(session: SessionDep) -> list[schemas.DescriptionTagMappingOut]:
    """List all description -> expense account mappings."""
    rows = services.list_mappings(session)
    return [
        schemas.DescriptionTagMappingOut(
            id=m.id,
            description=m.description,
            account_id=m.account_id,
            account_name=m.account.name if m.account else f"account:{m.account_id}",
        )
        for m in rows
    ]


@router.post("", response_model=schemas.DescriptionTagMappingOut)
def upsert_mapping(
    req: schemas.DescriptionTagMappingUpsert,
    session: SessionDep,
) -> schemas.DescriptionTagMappingOut:
    """Create or update a mapping: exact description -> expense account (splits are updated)."""
    try:
        m = services.upsert_mapping(session, req.description, req.account_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return schemas.DescriptionTagMappingOut(
        id=m.id,
        description=m.description,
        account_id=m.account_id,
        account_name=m.account.name if m.account else f"account:{m.account_id}",
    )


@router.delete("", status_code=200)
def delete_mapping_by_description(
    description: str,
    session: SessionDep,
) -> dict:
    """Remove a description-tag mapping by exact description (query param ?description=...)."""
    deleted = services.delete_mapping_by_description(session, description)
    if not deleted:
        raise HTTPException(404, detail="Mapping not found")
    return {"ok": True}


@router.delete("/{mapping_id}")
def delete_mapping(mapping_id: int, session: SessionDep) -> dict:
    """Remove a description-tag mapping by id."""
    deleted = services.delete_mapping(session, mapping_id)
    if not deleted:
        raise HTTPException(404, detail="Mapping not found")
    return {"ok": True}
