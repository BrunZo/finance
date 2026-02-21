"""
Transaction services: high-level operations for transfer/split patterns.
Amounts are positive; signs applied internally (debit +, credit -).
"""

from datetime import datetime, timezone
from decimal import Decimal
import uuid

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, Split, Transaction
from accounting.rest_api.description_tags import services as mapping_services


def _check_splits_balance(splits: list[tuple[int, Decimal]]) -> None:
    total = sum([amt for _, amt in splits])
    if total != 0:
        raise ValueError(f"Splits must sum to zero, got {total}")


def _check_account_id(account_id: int, session: Session) -> None:
    if session.query(Account).filter(Account.id == account_id).first() is None:
        raise ValueError(f"Account {account_id} not found")


def _check_splits_account_ids(splits: list[tuple[int, Decimal]], session: Session) -> None:
    missing_account_ids = []
    for account_id, _ in splits:
        try:
            _check_account_id(account_id, session)
        except ValueError:
            missing_account_ids.append(account_id)
    if missing_account_ids:
        raise ValueError(f"Account(s) {', '.join(str(x) for x in missing_account_ids)} do not exist")


def create_transaction(
    session: Session,
    description: str,
    splits: list[tuple[int, Decimal]],
    *,
    timestamp: datetime = datetime.now(timezone.utc),
    external_reference: str = f"api-{uuid.uuid4().hex}",
    currency: str = "USD",
) -> Transaction:
    _check_splits_balance(splits)
    _check_splits_account_ids(splits, session)
    tx = Transaction(
        description=description,
        timestamp=timestamp,
        external_reference=external_reference,
        currency=currency,
    )
    session.add(tx)
    session.flush()
    for account_id, amount in splits:
        session.add(Split(transaction_id=tx.id, account_id=account_id, amount=amount))
    return tx


def list_transactions(session: Session) -> list[Transaction]:
    tx_list = (
        session.query(Transaction)
        .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
        .all()
    )
    return tx_list


def list_uncategorized_transactions(session: Session) -> list[Transaction]:
    """List transactions with uncategorized splits (expense or income)."""
    tx_list = (
        session.query(Transaction)
        .join(Split, Transaction.id == Split.transaction_id)
        .join(Account, Split.account_id == Account.id)
        .filter(
            Account.tag == "uncategorized",
            Account.account_type.in_([AccountType.EXPENSE, AccountType.INCOME]),
        )
        .distinct()
        .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
        .all()
    )
    return tx_list


def update_split_account(session: Session, split_id: int, account_id: int) -> Split:
    _check_account_id(account_id, session)
    
    split = session.query(Split).filter(Split.id == split_id).first()
    if split is None:
        raise ValueError("Split not found")
    
    split.account_id = account_id
    session.flush()
    return split
