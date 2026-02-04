"""Seed default chart of accounts. Idempotent: skips accounts that already exist."""

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType

DEFAULT_ACCOUNTS = [
    (AccountType.ASSET, "bank"),
    (AccountType.ASSET, "reimbursements"),
    (AccountType.LIABILITY, "iou"),
    (AccountType.EXPENSE, "all"),
    (AccountType.EXPENSE, "dining"),
    (AccountType.INCOME, "all"),
]


def seed_accounts(session: Session) -> int:
    """
    Create default accounts if they do not exist.
    Returns the number of new accounts created.
    """
    created = 0
    for account_type, tag in DEFAULT_ACCOUNTS:
        existing = (
            session.query(Account)
            .filter(
                Account.account_type == account_type,
                Account.tag == tag,
            )
            .first()
        )
        if existing is None:
            session.add(Account(account_type=account_type, tag=tag))
            created += 1
    session.commit()
    return created


def create_account(session: Session, account_type: AccountType, tag: str) -> Account:
    """Create an account if it does not exist."""
    existing = (
        session.query(Account)
        .filter(Account.account_type == account_type, Account.tag == tag)
        .first()
    )
    if existing is None:
        session.add(Account(account_type=account_type, tag=tag))
        session.commit()
    return existing
