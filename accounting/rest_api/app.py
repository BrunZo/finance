"""
Web API for ledger: accounts, transactions, reports.
Run: uvicorn accounting.rest_api.app:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from accounting.db import get_session, init_db
from accounting.rest_api.accounts.routes import router as accounts_router
from accounting.rest_api.reports.routes import router as reports_router
from accounting.rest_api.transactions.routes import router as transactions_router


def _ensure_db() -> None:
    init_db()
    session = get_session()
    try:
        session.commit()
    finally:
        session.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ensure_db()
    yield


app = FastAPI(
    title="Ledger",
    description="Transfers & splits",
    lifespan=lifespan,
)

app.include_router(accounts_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
