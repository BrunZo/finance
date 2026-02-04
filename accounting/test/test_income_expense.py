"""
Example: salary income and rent expense.
Income increases Income:all; rent is Expense:all. Cleaned expenses show only rent.
"""

from decimal import Decimal

from sqlalchemy import func

from accounting.models import AccountType, Split, create_transaction
from accounting.reports import get_cleaned_expenses
from accounting.test.helpers import get_account_id, temporary_ledger_db, test_decimal


def get_balance(session, account_id: int) -> Decimal:
    """Sum of all split amounts for the given account."""
    result = session.query(func.coalesce(func.sum(Split.amount), 0)).filter(
        Split.account_id == account_id
    ).scalar()
    return Decimal(str(result))


def main() -> None:
    with temporary_ledger_db() as session:
        # Salary: bank +3000, income +3000
        bank = get_account_id(session, AccountType.ASSET, "bank")
        income_all = get_account_id(session, AccountType.INCOME, "all")
        create_transaction(
            session,
            "Salary",
            [
                (bank, Decimal("3000")),
                (income_all, -Decimal("3000")),
            ],
        )
        session.commit()

        # Rent: bank -1200, expense +1200
        bank = get_account_id(session, AccountType.ASSET, "bank")
        expense_all = get_account_id(session, AccountType.EXPENSE, "all")
        create_transaction(
            session,
            "Rent payment",
            [
                (bank, -Decimal("1200")),
                (expense_all, Decimal("1200")),
            ],
        )
        session.commit()

        report = get_cleaned_expenses(session)
        row = report[report["account_name"] == "expense:all"]
        test_decimal(row["amount"].iloc[0], Decimal("1200"))
        test_decimal(get_balance(session, bank), Decimal("1800"))
        
        print("[OK] example_salary_rent: cleaned expenses show expense:all = 1200")


if __name__ == "__main__":
    main()
