"""SQLAlchemy models for double-entry bookkeeping."""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, UniqueConstraint, Enum
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class AccountType(PyEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("account_type", "tag", name="uq_account_type_tag"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_type = Column(Enum(AccountType), nullable=False)
    tag = Column(String(64), nullable=False)

    splits = relationship("Split", back_populates="account")
    description_expense_mappings = relationship("DescriptionExpenseMapping", back_populates="expense_account")

    @property
    def name(self) -> str:
        return f"{self.account_type.value}:{self.tag}"

    def __repr__(self) -> str:
        return f"<Account {self.name}>"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("external_reference", name="uq_transaction_external_reference"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    external_reference = Column(String(256), nullable=False, unique=True)
    description = Column(String(256))

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


class DescriptionExpenseMapping(Base):
    __tablename__ = "description_expense_mappings"
    __table_args__ = (UniqueConstraint("description", name="uq_description_expense_description"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(256), nullable=False, unique=True)
    expense_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    expense_account = relationship("Account", back_populates="description_expense_mappings")

    def __repr__(self) -> str:
        return f"<DescriptionExpenseMapping {self.description!r} -> expense_account_id={self.expense_account_id}>"
