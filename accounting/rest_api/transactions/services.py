"""
Transaction services: high-level operations for transfer/split patterns.
Amounts are positive; signs applied internally (debit +, credit -).
"""

from decimal import Decimal
from typing import Sequence

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, create_transaction, Split, Transaction
from accounting.rest_api.accounts import services as account_services
from accounting.rest_api.description_tags import services as mapping_services


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


def create_expense(
    session: Session,
    description: str,
    source_account_id: int,
    expense_account_id: int,
    amount: Decimal,
) -> None:
    """Record an expense you paid yourself: money leaves source, goes to expense."""
    create_transaction(
        session,
        description,
        [
            (source_account_id, -amount),
            (expense_account_id, amount),
        ],
    )


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


def pay_for_many(
    session: Session,
    description: str,
    source_account_id: int,
    expense_account_id: int,
    total_amount: Decimal,
    my_share: Decimal,
    friend_amounts: Sequence[tuple[str | None, Decimal]],
) -> None:
    splits: list[tuple[int, Decimal]] = [
        (source_account_id, -total_amount),
        (expense_account_id, my_share),
    ]
    for friend_name, amount in friend_amounts:
        if amount <= 0:
            continue
        recv_id = get_or_create_receivable_account(session, friend_name or None)
        splits.append((recv_id, amount))
    create_transaction(session, description, splits)


def being_paid_for(
    session: Session,
    description: str,
    liability_account_id: int,
    expense_account_id: int,
    my_share: Decimal,
) -> None:
    create_transaction(
        session,
        description,
        [
            (liability_account_id, -my_share),
            (expense_account_id, my_share),
        ],
    )


def receive_receivable(
    session: Session,
    description: str,
    amount: Decimal,
    from_receivable_account_id: int,
    to_bank_account_id: int,
) -> None:
    create_transaction(
        session,
        description,
        [
            (to_bank_account_id, amount),
            (from_receivable_account_id, -amount),
        ],
    )


def pay_payable(
    session: Session,
    description: str,
    amount: Decimal,
    payable_account_id: int,
    from_bank_account_id: int,
) -> None:
    create_transaction(
        session,
        description,
        [
            (from_bank_account_id, -amount),
            (payable_account_id, amount),
        ],
    )
