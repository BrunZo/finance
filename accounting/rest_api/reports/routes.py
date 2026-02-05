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
    return services.get_expenses_rows(session)
