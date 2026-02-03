"""
Example: salary income and rent expense.
Income increases Income:all; rent is Expense:all. Cleaned expenses show only rent.
"""

from decimal import Decimal

from accounting.reports import get_cleaned_expenses
from accounting.test.examples import rent_payment, salary_income
from accounting.test.helpers import temporary_ledger_db


def main() -> None:
    with temporary_ledger_db() as session:
        # Salary: bank +3000, income +3000
        salary_income(session, Decimal("3000"))

        # Rent: bank -1200, expense +1200
        rent_payment(session, Decimal("1200"))

        report = get_cleaned_expenses(session)
        row = report[report["account_name"] == "expense:all"]
        assert not row.empty and row["amount"].iloc[0] == 1200
        print("[OK] example_salary_rent: cleaned expenses show expense:all = 1200")


if __name__ == "__main__":
    main()
