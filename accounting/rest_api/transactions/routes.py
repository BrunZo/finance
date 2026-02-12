"""Transactions API: list transactions, create from splits."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from accounting.rest_api.deps import get_db
from accounting.rest_api.helpers import try_run
from accounting.rest_api.transactions import schemas, services

router = APIRouter(prefix="/transactions", tags=["transactions"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/splits", response_model=schemas.TransactionOut)
def create_splits(req: schemas.SplitsRequest, session: SessionDep) -> schemas.TransactionOut:
    splits_tuples = [(s.account_id, s.amount) for s in req.splits]
    tx = try_run(
        services.create_transaction,
        session,
        req.description,
        splits_tuples,
        currency=req.currency,
    )
    return schemas.TransactionOut.model_validate(tx)


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(session: SessionDep) -> list[schemas.TransactionOut]:
    tx_list = services.list_transactions(session)
    return [schemas.TransactionOut.model_validate(tx) for tx in tx_list]


@router.get("/uncategorized", response_model=list[schemas.TransactionOut])
def list_uncategorized_transactions(session: SessionDep) -> list[schemas.TransactionOut]:
    tx_list = services.list_uncategorized_transactions(session)
    return [schemas.TransactionOut.model_validate(tx) for tx in tx_list]


@router.patch("/splits/{split_id}", response_model=schemas.SplitOut)
def update_split(
    split_id: int,
    req: schemas.SplitUpdate,
    session: SessionDep,
) -> schemas.SplitOut:
    split = try_run(services.update_split_account, session, split_id, req.account_id)
    return schemas.SplitOut.model_validate(split)
