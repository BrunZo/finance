"""SQLAlchemy models for double-entry bookkeeping."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, UniqueConstraint, Enum
from sqlalchemy.orm import DeclarativeBase, relationship


class AccountType(PyEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("account_type", "tag", name="uq_account_type_tag"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_type = Column(Enum(AccountType), nullable=False)
    tag = Column(String(64), nullable=False)

    splits = relationship("Split", back_populates="account")

    @property
    def name(self) -> str:
        return f"{self.account_type.value}:{self.tag}"

    def __repr__(self) -> str:
        return f"<Account {self.name}>"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("ext_ref", name="uq_transaction_ext_ref"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    description = Column(String(256))
    ext_ref = Column(String(256), nullable=True, unique=True)

    splits = relationship("Split", back_populates="transaction", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} {self.description!r}>"


class Split(Base):
    __tablename__ = "splits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)  # Debit positive, Credit negative

    transaction = relationship("Transaction", back_populates="splits")
    account = relationship("Account", back_populates="splits")

    def __repr__(self) -> str:
        return f"<Split account_id={self.account_id} amount={self.amount}>"


def _check_splits_balance(splits: list[tuple[int, Decimal]]) -> None:
    """Raise ValueError if sum of amounts is not zero (invalid double-entry transaction)."""
    total = sum([amt for _, amt in splits])
    if total != 0:
        raise ValueError(f"Splits must sum to zero, got {total}")


def _check_splits_account_ids(splits: list[tuple[int, Decimal]], session) -> None:
    """Raise ValueError if any account id does not exist."""
    missing_account_ids = []
    for account_id, _ in splits:
        if session.query(Account).filter(Account.id == account_id).first() is None:
            missing_account_ids.append(account_id)
    if missing_account_ids:
        raise ValueError(f"Account(s) {', '.join(missing_account_ids)} do not exist")


def create_transaction(
    session,
    description: str,
    splits: list[tuple[int, Decimal]],
    *,
    timestamp: datetime | None = None,
    ext_ref: str | None = None,
) -> Transaction:
    """
    Create a transaction with the given splits. Raises ValueError if splits do not sum to zero.
    splits: list of (account_id, amount) with amount positive for Debit, negative for Credit.
    ext_ref: optional external reference (e.g. statement ref) for deduplication; must be unique if set.
    """
    _check_splits_balance(splits)
    _check_splits_account_ids(splits, session)

    if not timestamp:
        timestamp = datetime.now(timezone.utc)

    tx = Transaction(description=description, timestamp=timestamp, ext_ref=ext_ref or None)
    session.add(tx)
    session.flush()
    for account_id, amount in splits:
        session.add(
            Split(transaction_id=tx.id, account_id=account_id, amount=amount)
        )
    return tx
