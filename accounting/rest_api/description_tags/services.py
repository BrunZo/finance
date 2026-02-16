"""Services for description -> account mappings (any account type)."""

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, DescriptionAccountMapping, Transaction


def _check_account(session: Session, account_id: int) -> Account:
    account = session.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise ValueError(f"Account {account_id} not found")
    return account


def _apply_mapping_to_transactions(session: Session, description: str, account_id: int) -> None:
    """
    Update transactions with matching description: set the categorizable split
    to the mapped account. Updates: expense/income/liability splits, or asset splits
    with tag 'uncategorized' (e.g. transfers).
    """
    if not (description and description.strip()):
        return
    transactions = (
        session.query(Transaction)
        .filter(Transaction.description == description.strip())
        .all()
    )
    for tx in transactions:
        for split in tx.splits:
            if split.account_id == account_id:
                continue
            if not split.account:
                continue
            # Update categorizable splits: non-asset, or asset:uncategorized (transfers)
            is_categorizable = (
                split.account.account_type != AccountType.ASSET
                or split.account.tag == "uncategorized"
                or split.account.tag.startswith("uncategorized:")
            )
            if is_categorizable:
                split.account_id = account_id
    session.flush()


def insert_mapping(
    session: Session,
    description: str,
    account_id: int,
) -> DescriptionAccountMapping:
    account = _check_account(session, account_id)
    m = DescriptionAccountMapping(description=description, account=account)
    session.add(m)
    session.flush()
    _apply_mapping_to_transactions(session, description, account_id)
    return m


def list_mappings(session: Session) -> list[DescriptionAccountMapping]:
    return (
        session.query(DescriptionAccountMapping)
        .order_by(DescriptionAccountMapping.description)
        .all()
    )


def mapping_by_description(session: Session, description: str) -> DescriptionAccountMapping:
    return (
        session.query(DescriptionAccountMapping)
        .filter(DescriptionAccountMapping.description == description)
        .first()
    )


def update_mapping(
    session: Session,
    description: str,
    account_id: int,
) -> DescriptionAccountMapping:
    account = _check_account(session, account_id)
    m = session.query(DescriptionAccountMapping).filter(DescriptionAccountMapping.description == description).first()
    if m is None:
        raise ValueError(f"Description {description} not found")
    m.account = account
    session.flush()
    _apply_mapping_to_transactions(session, description, account_id)
    return m


def update_mapping_by_id(session: Session, mapping_id: int, account_id: int) -> DescriptionAccountMapping:
    m = session.query(DescriptionAccountMapping).filter(DescriptionAccountMapping.id == mapping_id).first()
    if m is None:
        raise ValueError(f"Mapping {mapping_id} not found")
    account = _check_account(session, account_id)
    m.account = account
    session.flush()
    _apply_mapping_to_transactions(session, m.description, account_id)
    return m


def upsert_mapping(session: Session, description: str, account_id: int) -> DescriptionAccountMapping:
    m = session.query(DescriptionAccountMapping).filter(DescriptionAccountMapping.description == description).first()
    if m is None:
        return insert_mapping(session, description, account_id)
    return update_mapping(session, description, account_id)


def delete_mapping(session: Session, mapping_id: int) -> bool:
    m = session.query(DescriptionAccountMapping).filter(DescriptionAccountMapping.id == mapping_id).first()
    if m is None:
        return False
    session.delete(m)
    return m
