"""Account services: list, get-or-create, delete."""

from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, Split


def list_accounts(session: Session) -> list[Account]:
    """Return all accounts ordered by type and tag."""
    return (
        session.query(Account)
        .order_by(Account.account_type, Account.tag)
        .all()
    )


def get_balance(
    session: Session,
    account_id: int,
) -> Decimal:
    """Return balance for account id. Balance = sum of split amounts."""
    row = (
        session.query(func.coalesce(func.sum(Split.amount), 0))
        .filter(Split.account_id == account_id)
        .scalar()
    )
    return Decimal(row) if row is not None else Decimal(0)


def get_or_create_account(
    session: Session,
    account_type: AccountType,
    tag: str,
) -> Account:
    """Get or create an account. Returns the account."""
    existing = (
        session.query(Account)
        .filter(Account.account_type == account_type, Account.tag == tag)
        .first()
    )
    if existing is not None:
        return existing
    acc = Account(account_type=account_type, tag=tag)
    session.add(acc)
    session.flush()
    return acc


def delete_account(session: Session, account_id: int) -> bool:
    """Delete an account by id. Returns True if deleted. Caller must commit."""
    acc = session.query(Account).filter(Account.id == account_id).first()
    if acc is None:
        return False
    session.delete(acc)
    return True
