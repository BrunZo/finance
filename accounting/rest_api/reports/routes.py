"""Reports API: expenses and other reports."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from accounting.rest_api.deps import get_db
from accounting.rest_api.reports import schemas, services

router = APIRouter(prefix="/reports", tags=["reports"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.get("/expenses", response_model=list[schemas.ExpenseRow])
def report_expenses(session: SessionDep) -> list[schemas.ExpenseRow]:
    rows = services.get_expenses_rows(session)
    return [schemas.ExpenseRow.model_validate(row) for row in rows]


@router.get("/expenses-tree", response_model=schemas.ExpenseTreeResponse)
def report_expenses_tree(session: SessionDep) -> schemas.ExpenseTreeResponse:
    tree = services.get_expenses_tree(session)
    return schemas.ExpenseTreeResponse.model_validate(tree)


@router.get("/balances-by-currency", response_model=list[schemas.BalanceByCurrencyRow])
def report_balances_by_currency(session: SessionDep) -> list[schemas.BalanceByCurrencyRow]:
    rows = services.get_balances_by_currency(session)
    return [schemas.BalanceByCurrencyRow.model_validate(row) for row in rows]
