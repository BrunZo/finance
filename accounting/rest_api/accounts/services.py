"""Account services: list, get-or-create, delete."""

from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, Split


def insert_account(session: Session, account_type: AccountType, tag: str) -> Account:
    account = Account(account_type=account_type, tag=tag)
    session.add(account)
    session.flush()
    return account


def list_accounts(session: Session) -> list[Account]:
    return (
        session.query(Account)
        .order_by(Account.account_type, Account.tag)
        .all()
    )


def account_by_name(
    session: Session,
    account_type: AccountType,
    tag: str,
) -> Account:
    return (
        session.query(Account)
        .filter(Account.account_type == account_type, Account.tag == tag)
        .first()
    )


def balance(
    session: Session,
    account_id: int,
) -> Decimal:
    row = (
        session.query(func.coalesce(func.sum(Split.amount), 0))
        .filter(Split.account_id == account_id)
        .scalar()
    )
    return Decimal(row) if row is not None else Decimal(0)


def update_account(session: Session, account_id: int, account_type: AccountType, tag: str) -> Account:
    account = session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise ValueError(f"Account {account_id} not found")
    account.account_type = account_type
    account.tag = tag
    session.flush()
    return account


def upsert_account(session: Session, account_type: AccountType, tag: str) -> Account:
    account = session.query(Account).filter(Account.account_type == account_type, Account.tag == tag).first()
    if account is None:
        return insert_account(session, account_type, tag)
    return update_account(session, account.id, account_type, tag)


def delete_account(session: Session, account_id: int) -> bool:
    account = session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        return False
    session.delete(account)
    session.flush()
    return True
