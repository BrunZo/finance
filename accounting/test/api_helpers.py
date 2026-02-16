"""Helpers for tests that run against the REST API with an ephemeral DB."""

from __future__ import annotations

from decimal import Decimal
import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from accounting.models import Base

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


@contextmanager
def temporary_api_client() -> Iterator[TestClient]:
    """
    Create a temporary DB, override the app's get_db to use it, yield a FastAPI TestClient.
    Each test gets its own ephemeral DB; create accounts via POST /api/accounts.
    The app's lifespan still runs with the default DB; all request handlers use this temp DB.
    """
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "ledger.db")
    try:
        engine = create_engine(
            f"sqlite:///{path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine, autoflush=True)

        def overridden_get_db():
            session = SessionLocal()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

        from accounting.rest_api import deps
        from accounting.rest_api.app import app
        from fastapi.testclient import TestClient

        app.dependency_overrides[deps.get_db] = overridden_get_db
        try:
            with TestClient(app) as client:
                yield client
        finally:
            app.dependency_overrides.pop(deps.get_db, None)
    finally:
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)


def create_account(
    client: TestClient,
    account_type: str,
    tag: str,
) -> dict:
    r = client.post("/api/accounts", json={"account_type": account_type, "tag": tag})
    r.raise_for_status()
    return r.json()


def get_balance(client: TestClient, account_id: int) -> Decimal:
    r = client.get(f"/api/accounts/{account_id}")
    r.raise_for_status()
    return Decimal(r.json())


def account_id_by_tag(client: TestClient, tag: str) -> int:
    r = client.get("/api/accounts")
    r.raise_for_status()
    for a in r.json():
        if a["tag"] == tag:
            return a["id"]
    raise KeyError(tag)


def post_splits(
    client: TestClient,
    description: str,
    splits: list[tuple[int, str]],
) -> None:
    payload = {
        "description": description,
        "splits": [{"account_id": aid, "amount": amt} for aid, amt in splits],
    }
    r = client.post("/api/transactions/splits", json=payload)
    r.raise_for_status()


def get_expenses_report(client: TestClient) -> list[dict]:
    r = client.get("/api/reports/expenses")
    r.raise_for_status()
    return r.json()
