"""Transactions API: expense, pay-for-many, being-paid-for, receive-receivable, pay-payable, splits."""

from decimal import Decimal
from typing import Annotated, Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from accounting.rest_api.deps import get_db
from accounting.rest_api.transactions import schemas, services

router = APIRouter(prefix="/transactions", tags=["transactions"])
SessionDep = Annotated[Session, Depends(get_db)]


def _parse_decimal(value: str, param: str = "amount") -> Decimal:
    try:
        return Decimal(value)
    except Exception as e:
        raise HTTPException(422, detail=f"Invalid {param}: {e}")


def _run(fn: Callable[..., None], *args, **kwargs) -> dict:
    try:
        fn(*args, **kwargs)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(session: SessionDep) -> list[schemas.TransactionOut]:
    """List all transactions with their splits and account names (for debugging import)."""
    rows = services.list_all_transactions_with_splits(session)
    return [schemas.TransactionOut(**r) for r in rows]


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


@router.post("/expense")
def create_expense(
    req: schemas.Expense,
    session: SessionDep,
) -> dict:
    """Record an expense you paid yourself (e.g. from bank to dining)."""
    amount = _parse_decimal(req.amount)
    return _run(
        services.create_expense,
        session,
        req.description,
        req.source_account_id,
        req.expense_account_id,
        amount,
    )


@router.post("/pay-for-many")
def pay_for_many(req: schemas.PayForManyRequest, session: SessionDep) -> dict:
    total = _parse_decimal(req.total_amount, "total_amount")
    my_share = _parse_decimal(req.my_share, "my_share")
    friend_amounts = [
        (f.friend_name, _parse_decimal(f.amount, "friend amount"))
        for f in req.friend_amounts
    ]
    return _run(
        services.pay_for_many,
        session,
        req.description,
        req.source_account_id,
        req.expense_account_id,
        total,
        my_share,
        friend_amounts,
    )


@router.post("/being-paid-for")
def being_paid_for(req: schemas.BeingPaidForRequest, session: SessionDep) -> dict:
    my_share = _parse_decimal(req.my_expense_share, "my_expense_share")
    return _run(
        services.being_paid_for,
        session,
        req.description,
        req.liability_account_id,
        req.expense_account_id,
        my_share,
    )


@router.post("/receive-receivable")
def receive_receivable(
    req: schemas.ReceiveReceivableRequest,
    session: SessionDep,
) -> dict:
    amount = _parse_decimal(req.amount)
    return _run(
        services.receive_receivable,
        session,
        req.description,
        amount,
        req.from_receivable_account_id,
        req.to_bank_account_id,
    )


@router.post("/pay-payable")
def pay_payable(req: schemas.PayPayableRequest, session: SessionDep) -> dict:
    amount = _parse_decimal(req.amount)
    return _run(
        services.pay_payable,
        session,
        req.description,
        amount,
        req.payable_account_id,
        req.from_bank_account_id,
    )
