"""
Example: post a few transactions and assert account balances (sum of splits per account).
Shows that double-entry keeps every account's balance consistent.
"""

from decimal import Decimal

from sqlalchemy import func

from accounting.models import AccountType, Split
from accounting.reports import get_cleaned_expenses
from accounting.test.examples import friend_reimbursement, split_dinner
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
        split_dinner(session, [Decimal("50"), Decimal("50"), Decimal("50")])

        assert get_balance(session, bank) == Decimal("-150")
        assert get_balance(session, reimbursements) == Decimal("100")
        assert get_balance(session, dining) == Decimal("50")

        # Dinner 120 (you 40, friend 80)
        split_dinner(session, [Decimal("40"), Decimal("80")])

        assert get_balance(session, bank) == Decimal("-270")
        assert get_balance(session, reimbursements) == Decimal("180")
        assert get_balance(session, dining) == Decimal("90")

        # Friends reimburse their dinners
        friend_reimbursement(session, Decimal("130"))
        friend_reimbursement(session, Decimal("50"))

        assert get_balance(session, bank) == Decimal("-90")
        assert get_balance(session, reimbursements) == Decimal("0")
        assert get_balance(session, dining) == Decimal("90")

        report = get_cleaned_expenses(session)
        assert report[report["account_name"] == "expense:dining"]["amount"].iloc[0] == 90
        
        print("[OK] example_dinners: balances consistent after dinner and reimbursement")


if __name__ == "__main__":
    main()
