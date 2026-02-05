"""
Example: salary income and rent expense.
Same scenario as before, now via the REST API with an ephemeral DB.
"""

from decimal import Decimal

from accounting.test.api_helpers import (
    temporary_api_client,
    create_account,
    get_balance,
    post_splits,
    get_expenses_report,
)


def main() -> None:
    with temporary_api_client() as client:
        bank = create_account(client, "asset", "bank")
        income_all = create_account(client, "income", "all")
        expense_all = create_account(client, "expense", "all")

        # Salary: bank +3000, income -3000
        post_splits(
            client,
            "Salary",
            [
                (bank["id"], "3000"),
                (income_all["id"], "-3000"),
            ],
        )

        # Rent: bank -1200, expense +1200
        post_splits(
            client,
            "Rent payment",
            [
                (bank["id"], "-1200"),
                (expense_all["id"], "1200"),
            ],
        )

        report = get_expenses_report(client)
        row = next(r for r in report if r["account_name"] == "expense:all")
        assert row["amount"] == 1200
        assert get_balance(client, bank["id"]) == 1800

        print("[OK] test_income_expense: cleaned expenses show expense:all = 1200")


if __name__ == "__main__":
    main()
