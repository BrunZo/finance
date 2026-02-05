"""Accounts API: list and create accounts."""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from accounting.models import AccountType
from accounting.rest_api.accounts import schemas, services
from accounting.rest_api.deps import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])
SessionDep = Annotated[Session, Depends(get_db)]


def _try_parse_account_type(account_type: str) -> AccountType:
    try:
        return AccountType(account_type)
    except ValueError:
        raise HTTPException(422, detail=f"Invalid account type: {account_type}")


@router.get("", response_model=list[schemas.AccountOut])
def list_accounts(
    session: SessionDep,
) -> list[schemas.AccountOut]:
    accounts = services.list_accounts(session)
    return [schemas.AccountOut.from_account(acc) for acc in accounts]


@router.get("/{account_id}")
def get_balance(
    session: SessionDep,
    account_id: int,
) -> Decimal:
    balance = services.get_balance(session, account_id)
    return balance


@router.post("", response_model=schemas.AccountOut)
def create_account(
    req: schemas.AccountCreate,
    session: SessionDep,
) -> schemas.AccountOut:
    account = services.get_or_create_account(
        session,
        _try_parse_account_type(req.account_type),
        req.tag,
    )
    return schemas.AccountOut.from_account(account)


@router.delete("/{account_id}")
def delete_account(account_id: int, session: SessionDep) -> dict:
    deleted = services.delete_account(session, account_id)
    if not deleted:
        raise HTTPException(404, detail="Account not found")
    return {"ok": True}
