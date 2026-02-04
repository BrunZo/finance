"""
Example: post a few transactions and assert account balances (sum of splits per account).
Shows that double-entry keeps every account's balance consistent.
"""

from decimal import Decimal

from sqlalchemy import func

from accounting.models import AccountType, Split, create_transaction
from accounting.reports import get_cleaned_expenses
from accounting.seed_accounts import create_account
from accounting.test.helpers import get_account_id, temporary_ledger_db, test_decimal


def get_balance(session, account_id: int) -> Decimal:
    """Sum of all split amounts for the given account."""
    result = session.query(func.coalesce(func.sum(Split.amount), 0)).filter(
        Split.account_id == account_id
    ).scalar()
    return Decimal(str(result))


def main() -> None:
    with temporary_ledger_db() as session:

        create_account(session, AccountType.ASSET, "bank")
        create_account(session, AccountType.ASSET, "reimbursements")
        create_account(session, AccountType.LIABILITY, "iou")
        create_account(session, AccountType.EXPENSE, "dining")
        create_account(session, AccountType.EXPENSE, "bowling")
        create_account(session, AccountType.EXPENSE, "oil")
        
        bank = get_account_id(session, AccountType.ASSET, "bank")
        reimbursements = get_account_id(session, AccountType.ASSET, "reimbursements")
        iou = get_account_id(session, AccountType.LIABILITY, "iou")
        dining = get_account_id(session, AccountType.EXPENSE, "dining")
        bowling = get_account_id(session, AccountType.EXPENSE, "bowling")
        oil = get_account_id(session, AccountType.EXPENSE, "oil")

        # Bowling 60 total for 5 people
        create_transaction(session, "Bowling", [
            (iou, -Decimal("60")),
            (bowling, Decimal("12")),
            (reimbursements, Decimal("48")),
        ])

        # Dinner for myself
        create_transaction(session, "Bowling", [
            (iou, -Decimal("27")),
            (dining, Decimal("27")),
        ])

        # Parents reimbursement
        create_transaction(session, "Parents reimbursement", [
            (bank, -Decimal("87")),
            (iou, Decimal("87")),
        ])

        # Oil payment
        create_transaction(session, "Oil payment", [
            (bank, -Decimal("70")),
            (reimbursements, Decimal("70")),
            (oil, Decimal("0")),
        ])

        # Friends reimbursement
        create_transaction(session, "Friends reimbursement", [
            (bank, Decimal("48")),
            (reimbursements, -Decimal("48")),
        ])
        
        session.commit()

        test_decimal(get_balance(session, bank), Decimal("-109"))
        test_decimal(get_balance(session, iou), Decimal("0"))
        test_decimal(get_balance(session, reimbursements), Decimal("70"))
        test_decimal(get_balance(session, dining), Decimal("27"))
        test_decimal(get_balance(session, bowling), Decimal("12"))
        test_decimal(get_balance(session, oil), Decimal("0"))

        report = get_cleaned_expenses(session)
        test_decimal(report['amount'].sum(), Decimal("39"))
        
        print("[OK] example_night: balances consistent after dinner and reimbursement")


if __name__ == "__main__":
    main()
