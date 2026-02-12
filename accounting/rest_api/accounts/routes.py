"""Accounts API: list and create accounts."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from accounting.rest_api.accounts import schemas, services
from accounting.rest_api.deps import get_db
from accounting.rest_api.helpers import try_run

router = APIRouter(prefix="/accounts", tags=["accounts"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("", response_model=schemas.AccountOut)
def insert_account(
    session: SessionDep,
    req: schemas.AccountUpsert,
) -> schemas.AccountOut:
    account = services.insert_account(session, req.to_account_type(), req.tag)
    return schemas.AccountOut.model_validate(account)


@router.get("", response_model=list[schemas.AccountOut])
def list_accounts(
    session: SessionDep,
) -> list[schemas.AccountOut]:
    accounts = services.list_accounts(session)
    return [schemas.AccountOut.model_validate(acc) for acc in accounts]


@router.get("/{account_id}")
def balance(
    session: SessionDep,
    account_id: int,
) -> Decimal:
    balance = services.balance(session, account_id)
    return balance


@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(
    session: SessionDep,
    account_id: int,
    req: schemas.AccountUpsert,
) -> schemas.AccountOut:
    account = try_run(services.update_account, session, account_id, req.to_account_type(), req.tag)
    return schemas.AccountOut.model_validate(account)


@router.delete("/{account_id}")
def delete_account(
    session: SessionDep,
    account_id: int,
) -> dict:
    deleted = services.delete_account(session, account_id)
    if not deleted:
        raise HTTPException(404, detail="Account not found")
    return {"ok": True}
