"""
Example: post a few transactions and assert account balances (sum of splits per account).
Shows that double-entry keeps every account's balance consistent.
"""

from decimal import Decimal
from typing import List

from sqlalchemy import func

from accounting.models import AccountType, Split, create_transaction
from accounting.reports import get_cleaned_expenses
from accounting.test.helpers import get_account_id, temporary_ledger_db


def get_balance(session, account_id: int) -> Decimal:
    """Sum of all split amounts for the given account."""
    result = session.query(func.coalesce(func.sum(Split.amount), 0)).filter(
        Split.account_id == account_id
    ).scalar()
    return Decimal(str(result))


def main() -> None:
    with temporary_ledger_db() as session:
        bank = get_account_id(session, AccountType.ASSET, "bank")
        reimbursements = get_account_id(session, AccountType.ASSET, "reimbursements")
        dining = get_account_id(session, AccountType.EXPENSE, "dining")

        # Dinner 150 (you 50, friend 50, friend 50)
        create_transaction(
            session,
            "Dinner with friends",
            [
                (bank, -Decimal("150")),
                (dining, Decimal("50")),
                (reimbursements, Decimal("100")),
            ],
        )
        session.commit()

        assert get_balance(session, bank) == Decimal("-150")
        assert get_balance(session, reimbursements) == Decimal("100")
        assert get_balance(session, dining) == Decimal("50")

        create_transaction(
            session,
            "Reimbursement",
            [
                (bank, Decimal("100")),
                (reimbursements, -Decimal("100")),
            ],
        )
        session.commit()
    
        assert get_balance(session, bank) == Decimal("-50")
        assert get_balance(session, reimbursements) == Decimal("0")
        assert get_balance(session, dining) == Decimal("50")

        report = get_cleaned_expenses(session)
        assert report[report["account_name"] == "expense:dining"]["amount"].iloc[0] == 50
        
        print("[OK] example_dinners: balances consistent after dinner and reimbursement")


if __name__ == "__main__":
    main()
