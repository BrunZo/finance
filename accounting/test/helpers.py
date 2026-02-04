"""Shared helpers for test examples."""

from decimal import Decimal
import os
import tempfile
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from accounting.models import Base, Account, AccountType
from accounting.seed_accounts import seed_accounts


def get_account_id(session: Session, account_type: AccountType, tag: str) -> int:
    """Return the id of the account with the given type and tag."""
    acc = (
        session.query(Account)
        .filter(
            Account.account_type == account_type,
            Account.tag == tag,
        )
        .one()
    )
    return acc.id


@contextmanager
def temporary_ledger_db() -> Iterator[Session]:
    """
    Create a temporary DB file, create tables, seed accounts, yield a session,
    then close and remove the DB file. Each test should use this so it gets its
    own DB and cleans up after.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        engine = create_engine(
            f"sqlite:///{path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine, autoflush=True)
        session = SessionLocal()
        seed_accounts(session)
        try:
            yield session
        finally:
            session.close()
        engine.dispose()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_decimal(x: Decimal, y: Decimal) -> None:
    assert x == y, f"Expected {y} but found {x}"
