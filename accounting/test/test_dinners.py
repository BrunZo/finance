"""
Example: post a few transactions and assert account balances (sum of splits per account).
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
        receivables = create_account(client, "asset", "receivables")
        dining = create_account(client, "expense", "dining")

        # Dinner 150 (you 50, friend 50, friend 50)
        post_splits(
            client,
            "Dinner with friends",
            [
                (bank["id"], "-150"),
                (dining["id"], "50"),
                (receivables["id"], "100"),
            ],
        )

        assert get_balance(client, bank["id"]) == -150
        assert get_balance(client, receivables["id"]) == 100
        assert get_balance(client, dining["id"]) == 50

        post_splits(
            client,
            "Reimbursement",
            [
                (bank["id"], "100"),
                (receivables["id"], "-100"),
            ],
        )

        assert get_balance(client, bank["id"]) == -50
        assert get_balance(client, receivables["id"]) == 0
        assert get_balance(client, dining["id"]) == 50

        report = get_expenses_report(client)
        dining_row = next(r for r in report if r["account_name"] == "expense:dining")
        assert dining_row["amount"] == 50

        print("[OK] test_dinners: balances consistent after dinner and reimbursement")


if __name__ == "__main__":
    main()
