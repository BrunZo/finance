"""Services for description -> expense account mappings."""

from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, DescriptionExpenseMapping, Transaction


def _check_expense_account(session: Session, expense_account_id: int) -> Account:
    account = session.query(Account).filter(Account.id == expense_account_id).first()
    if account is None:
        raise ValueError(f"Account {expense_account_id} not found")
    if account.account_type != AccountType.EXPENSE:
        raise ValueError(f"Account {expense_account_id} is not an expense account")
    return account


def _apply_mapping_to_transactions(session: Session, description: str, expense_account_id: int) -> None:
    if not (description and description.strip()):
        return
    transactions = (
        session.query(Transaction)
        .filter(Transaction.description == description.strip())
        .all()
    )
    for tx in transactions:
        for split in tx.splits:
            if (
                split.account
                and split.account.account_type == AccountType.EXPENSE
                and split.account_id != expense_account_id
            ):
                split.account_id = expense_account_id
    session.flush()


def insert_mapping(
    session: Session,
    description: str,
    expense_account_id: int,
) -> DescriptionExpenseMapping:
    expense_account = _check_expense_account(session, expense_account_id)
    m = DescriptionExpenseMapping(description=description, expense_account=expense_account)
    session.add(m)
    session.flush()
    _apply_mapping_to_transactions(session, description, expense_account_id)
    return m


def list_mappings(session: Session) -> list[DescriptionExpenseMapping]:
    return (
        session.query(DescriptionExpenseMapping)
        .order_by(DescriptionExpenseMapping.description)
        .all()
    )


def mapping_by_description(session: Session, description: str) -> DescriptionExpenseMapping:
    return (
        session.query(DescriptionExpenseMapping)
        .filter(DescriptionExpenseMapping.description == description)
        .first()
    )


def update_mapping(
    session: Session,
    description: str,
    expense_account_id: int,
) -> DescriptionExpenseMapping:
    expense_account = _check_expense_account(session, expense_account_id)
    m = session.query(DescriptionExpenseMapping).filter(DescriptionExpenseMapping.description == description).first()
    if m is None:
        raise ValueError(f"Description {description} not found")
    m.expense_account = expense_account
    session.flush()
    _apply_mapping_to_transactions(session, description, expense_account_id)
    return m


def update_mapping_by_id(session: Session, mapping_id: int, expense_account_id: int) -> DescriptionExpenseMapping:
    m = session.query(DescriptionExpenseMapping).filter(DescriptionExpenseMapping.id == mapping_id).first()
    if m is None:
        raise ValueError(f"Mapping {mapping_id} not found")
    expense_account = _check_expense_account(session, expense_account_id)
    m.expense_account = expense_account
    session.flush()
    _apply_mapping_to_transactions(session, m.description, expense_account_id)
    return m


def upsert_mapping(session: Session, description: str, expense_account_id: int) -> DescriptionExpenseMapping:
    m = session.query(DescriptionExpenseMapping).filter(DescriptionExpenseMapping.description == description).first()
    if m is None:
        return insert_mapping(session, description, expense_account_id)
    return update_mapping(session, description, expense_account_id)


def delete_mapping(session: Session, mapping_id: int) -> bool:
    m = session.query(DescriptionExpenseMapping).filter(DescriptionExpenseMapping.id == mapping_id).first()
    if m is None:
        return False
    session.delete(m)
    return m
