"""Database engine and session for the ledger."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from accounting.models import Base

# Default path; override with LEDGER_DB_PATH env var
DEFAULT_DB_PATH = "ledger.db"
DB_PATH = os.environ.get("LEDGER_DB_PATH", DEFAULT_DB_PATH)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)

Session = sessionmaker(bind=engine, autoflush=True)


def init_db() -> None:
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session():
    """Return a new session."""
    return Session()
