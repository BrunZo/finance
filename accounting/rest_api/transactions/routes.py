"""Transactions API: list transactions, create from splits."""

from decimal import Decimal
from typing import Annotated, Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from accounting.rest_api.deps import get_db
from accounting.rest_api.transactions import schemas, services

router = APIRouter(prefix="/transactions", tags=["transactions"])
SessionDep = Annotated[Session, Depends(get_db)]


def _run(fn: Callable[..., None], *args, **kwargs) -> dict:
    try:
        fn(*args, **kwargs)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(session: SessionDep) -> list[schemas.TransactionOut]:
    """List all transactions with their splits and account names."""
    rows = services.list_all_transactions_with_splits(session)
    return [schemas.TransactionOut(**r) for r in rows]


@router.get("/uncategorized-splits", response_model=list[schemas.UncategorizedSplitOut])
def list_uncategorized_splits(session: SessionDep) -> list[schemas.UncategorizedSplitOut]:
    """List expense splits that are still uncategorized."""
    rows = services.list_uncategorized_expense_splits(session)
    return [schemas.UncategorizedSplitOut(**r) for r in rows]


@router.post("/splits")
def create_splits(req: schemas.SplitsRequest, session: SessionDep) -> dict:
    """Create a transaction from raw splits. Amounts: positive=debit, negative=credit."""
    try:
        splits = [(s.account_id, Decimal(s.amount)) for s in req.splits]
    except Exception as e:
        raise HTTPException(422, detail=f"Invalid amounts: {e}")
    return _run(services.create_from_splits, session, req.description, splits)


@router.patch("/splits/{split_id}", response_model=schemas.SplitOut)
def update_split(
    split_id: int,
    req: schemas.SplitUpdate,
    session: SessionDep,
) -> schemas.SplitOut:
    try:
        split = services.update_split_account(session, split_id, req.account_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return schemas.SplitOut(
        id=split.id,
        account_id=split.account_id,
        account_name=split.account.name if split.account else f"account:{split.account_id}",
        amount=str(split.amount),
    )
