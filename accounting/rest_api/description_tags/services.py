"""Services for description -> expense account mappings."""

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, DescriptionTagMapping, Transaction
from accounting.rest_api.accounts import services as account_services


def apply_mapping_to_transactions(
    session: Session,
    description: str,
    account_id: int,
) -> int:
    """
    Update all transactions with this exact description: set their expense splits
    to the given expense account. Returns the number of splits updated.
    """
    description = description.strip()
    transactions = (
        session.query(Transaction)
        .filter(Transaction.description == description)
        .all()
    )
    updated = 0
    for tx in transactions:
        for split in tx.splits:
            if split.account is None:
                continue
            if split.account.account_type != AccountType.EXPENSE:
                continue
            if split.account_id != account_id:
                split.account_id = account_id
                updated += 1
    return updated


def list_mappings(session: Session) -> list[DescriptionTagMapping]:
    """Return all description-account mappings ordered by description."""
    return (
        session.query(DescriptionTagMapping)
        .order_by(DescriptionTagMapping.description)
        .all()
    )


def get_mapping_for_description(session: Session, description: str | None) -> DescriptionTagMapping | None:
    """Return the mapping row for an exact description match, or None (includes account via relationship)."""
    if not (description and description.strip()):
        return None
    return (
        session.query(DescriptionTagMapping)
        .filter(DescriptionTagMapping.description == description.strip())
        .first()
    )


def upsert_mapping(
    session: Session,
    description: str,
    account_id: int,
) -> DescriptionTagMapping:
    """
    Create or update mapping for this description to the given expense account,
    then update all transactions with that description so their expense splits use it.
    Raises ValueError if account does not exist or is not an expense account.
    Returns the mapping.
    """
    description = description.strip()
    account = session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise ValueError(f"Account {account_id} not found")
    if account.account_type != AccountType.EXPENSE:
        raise ValueError(f"Account {account_id} is not an expense account")
    existing = (
        session.query(DescriptionTagMapping)
        .filter(DescriptionTagMapping.description == description)
        .first()
    )
    if existing is not None:
        existing.account_id = account_id
        session.flush()
    else:
        m = DescriptionTagMapping(description=description, account_id=account_id)
        session.add(m)
        session.flush()
        existing = m
    apply_mapping_to_transactions(session, description, account_id)
    return existing


def delete_mapping(session: Session, mapping_id: int) -> bool:
    """Delete a mapping by id. Returns True if deleted."""
    m = session.query(DescriptionTagMapping).filter(DescriptionTagMapping.id == mapping_id).first()
    if m is None:
        return False
    session.delete(m)
    return True


def delete_mapping_by_description(session: Session, description: str) -> bool:
    """Delete a mapping by exact description. Returns True if deleted."""
    description = description.strip()
    m = (
        session.query(DescriptionTagMapping)
        .filter(DescriptionTagMapping.description == description)
        .first()
    )
    if m is None:
        return False
    session.delete(m)
    return True
