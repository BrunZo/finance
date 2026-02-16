"""
Example: post a few transactions and assert account balances.
Same scenario as before, now via the REST API with an ephemeral DB.
"""

from decimal import Decimal

from accounting.test.api_helpers import (
    create_account,
    get_balance,
    temporary_api_client,
    post_splits,
    get_expenses_report,
)


def test_decimal_api(actual: Decimal, expected: Decimal) -> None:
    assert abs(actual - expected) < 1e-9, f"Expected {expected} but found {actual}"


def main() -> None:
    with temporary_api_client() as client:
        bank = create_account(client, "asset", "bank")
        receivables = create_account(client, "asset", "receivables")
        payables = create_account(client, "liability", "payables")
        dining = create_account(client, "expense", "dining")
        bowling = create_account(client, "expense", "bowling")
        oil = create_account(client, "expense", "oil")

        # Bowling 60 total for 5 people
        post_splits(
            client,
            "Bowling",
            [
                (payables["id"], "-60"),
                (bowling["id"], "12"),
                (receivables["id"], "48"),
            ],
        )

        # Dinner for myself
        post_splits(
            client,
            "Bowling",
            [
                (payables["id"], "-27"),
                (dining["id"], "27"),
            ],
        )

        # Parents payable
        post_splits(
            client,
            "Parents payable",
            [
                (bank["id"], "-87"),
                (payables["id"], "87"),
            ],
        )

        # Oil payment
        post_splits(
            client,
            "Oil payment",
            [
                (bank["id"], "-70"),
                (receivables["id"], "70"),
                (oil["id"], "0"),
            ],
        )

        # Friends receivable
        post_splits(
            client,
            "Friends receivable",
            [
                (bank["id"], "48"),
                (receivables["id"], "-48"),
            ],
        )

        test_decimal_api(get_balance(client, bank["id"]), Decimal("-109"))
        test_decimal_api(get_balance(client, payables["id"]), Decimal("0"))
        test_decimal_api(get_balance(client, receivables["id"]), Decimal("70"))
        test_decimal_api(get_balance(client, dining["id"]), Decimal("27"))
        test_decimal_api(get_balance(client, bowling["id"]), Decimal("12"))
        test_decimal_api(get_balance(client, oil["id"]), Decimal("0"))

        report = get_expenses_report(client)
        total_expense = sum(r["amount"] for r in report)
        test_decimal_api(Decimal(total_expense), Decimal("39"))

        print("[OK] test_bowling: balances consistent after bowling and dinner")


if __name__ == "__main__":
    main()
