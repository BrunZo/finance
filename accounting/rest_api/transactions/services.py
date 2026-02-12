"""
Transaction services: high-level operations for transfer/split patterns.
Amounts are positive; signs applied internally (debit +, credit -).
"""

from datetime import datetime, timezone
from decimal import Decimal

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
    timestamp: datetime | None = None,
    external_reference: str | None = None,
) -> Transaction:
    _check_splits_balance(splits)
    _check_splits_account_ids(splits, session)

    if not timestamp:
        timestamp = datetime.now(timezone.utc)

    tx = Transaction(description=description, timestamp=timestamp, external_reference=external_reference)
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
    tx_list = (
        session.query(Transaction)
        .join(Split, Transaction.id == Split.transaction_id)
        .join(Account, Split.account_id == Account.id)
        .filter(Account.account_type == AccountType.EXPENSE, Account.tag.like("uncategorized:%"))
        .distinct()
        .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
        .all()
    )
    return tx_list


def update_split_account(session: Session, split_id: int, account_id: int) -> Split:
    split = session.query(Split).filter(Split.id == split_id).first()
    if split is None:
        raise ValueError("Split not found")

    _check_account_id(account_id, session)
    split.account_id = account_id
    session.flush()

    # Keep description->account mapping in sync when user manually changes an expense split
    if (
        split.account.account_type == AccountType.EXPENSE 
        and split.transaction.description
    ):
        mapping_services.upsert_mapping(session, split.transaction.description, account_id)

    auto_categorize(session)    
    return split


def auto_categorize(session: Session) -> None:
    for tx in list_uncategorized_transactions(session):
        mapping = mapping_services.mapping_by_description(session, tx.description)
        if not mapping:
            continue
        for split in tx.splits:
            if split.account.account_type == AccountType.EXPENSE and split.account.id != mapping.expense_account_id:
                update_split_account(session, split.id, mapping.expense_account_id)
