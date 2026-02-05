"""Shared FastAPI dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from accounting.db import get_session


def get_db() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
