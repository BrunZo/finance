"""
Transaction services: high-level operations for transfer/split patterns.
Amounts are positive; signs applied internally (debit +, credit -).
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, Split, Transaction
from accounting.rest_api.accounts import services as account_services
from accounting.rest_api.description_tags import services as mapping_services


def _check_splits_balance(splits: list[tuple[int, Decimal]]) -> None:
    """Raise ValueError if sum of amounts is not zero (invalid double-entry transaction)."""
    total = sum([amt for _, amt in splits])
    if total != 0:
        raise ValueError(f"Splits must sum to zero, got {total}")


def _check_splits_account_ids(splits: list[tuple[int, Decimal]], session: Session) -> None:
    """Raise ValueError if any account id does not exist."""
    missing_account_ids = []
    for account_id, _ in splits:
        if session.query(Account).filter(Account.id == account_id).first() is None:
            missing_account_ids.append(account_id)
    if missing_account_ids:
        raise ValueError(f"Account(s) {', '.join(str(x) for x in missing_account_ids)} do not exist")


def create_transaction(
    session: Session,
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


def _receivable_tag(friend_name: str | None) -> str:
    if not (friend_name and friend_name.strip()):
        return "receivables"
    return f"receivables:{friend_name.strip()}"


def _payable_tag(friend_name: str | None) -> str:
    if not (friend_name and friend_name.strip()):
        return "payables"
    return f"payables:{friend_name.strip()}"


def get_or_create_receivable_account(
    session: Session,
    friend_name: str | None = None,
) -> int:
    tag = _receivable_tag(friend_name)
    acc = account_services.get_or_create_account(session, AccountType.ASSET, tag)
    return acc.id


def get_or_create_payable_account(
    session: Session,
    friend_name: str | None = None,
) -> int:
    tag = _payable_tag(friend_name)
    acc = account_services.get_or_create_account(session, AccountType.LIABILITY, tag)
    return acc.id


def create_from_splits(
    session: Session,
    description: str,
    splits: list[tuple[int, Decimal]],
) -> None:
    """Create a transaction from raw splits. Amounts: positive=debit, negative=credit."""
    create_transaction(session, description, splits)


def list_all_transactions_with_splits(session: Session) -> list[dict]:
    """Return all transactions with splits (id, account, amount)."""
    tx_list = (
        session.query(Transaction)
        .order_by(Transaction.timestamp.desc(), Transaction.id.desc())
        .all()
    )
    out = []
    for tx in tx_list:
        splits_out = []
        for sp in tx.splits:
            name = sp.account.name if sp.account else f"account:{sp.account_id}"
            splits_out.append(
                {
                    "id": sp.id,
                    "account_id": sp.account_id,
                    "account_name": name,
                    "amount": str(sp.amount),
                }
            )
        out.append(
            {
                "id": tx.id,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "description": tx.description,
                "ext_ref": tx.ext_ref,
                "splits": splits_out,
            }
        )
    return out


def update_split_account(session: Session, split_id: int, account_id: int) -> Split:
    """Update a split's account. The new account must exist. Amount is unchanged (keeps transaction balanced).
    If the new account is an expense account and the transaction has a description, the description->account
    mapping is updated so it stays in sync. Returns the split."""
    split = session.query(Split).filter(Split.id == split_id).first()
    if split is None:
        raise ValueError("Split not found")
    new_account = session.query(Account).filter(Account.id == account_id).first()
    if new_account is None:
        raise ValueError(f"Account {account_id} not found")
    split.account_id = account_id
    session.flush()
    # Keep description->account mapping in sync when user manually changes an expense split
    if (
        new_account.account_type == AccountType.EXPENSE 
        and split.transaction.description
    ):
        mapping_services.upsert_mapping(session, split.transaction.description.strip(), account_id)
    return split
