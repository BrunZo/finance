"""
Load parsed statement CSVs into the ledger.

Expects CSVs produced by parsers.parse (columns: date, description, ref, currency, amount).
Amount: positive = outflow, negative = inflow.
Bank always gets amount; counter gets -amount. Positive → expense, negative → income.
"""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from accounting.models import AccountType, Transaction
from accounting.rest_api.accounts import services as account_services
from accounting.rest_api.transactions import services as transaction_services


# Parsed CSV columns (must match parsers.parse.PARSED_HEADER)
PARSED_HEADER = ["date", "description", "ref", "currency", "amount"]


def load_parsed_csv(
    csv_path: Path | str,
    session: Session,
    *,
    bank_tag: str = "unspecified",
    expense_tag: str = "uncategorized",
    income_tag: str = "uncategorized",
    skip_duplicates: bool = True,
) -> int:
    """
    Load a parsed statement CSV into the ledger.

    - csv_path: path to a parsed CSV (columns: date, description, ref, currency, amount).
    - session: SQLAlchemy session (caller commits).
    - bank_tag: base tag for the asset account -> asset:{bank_tag}.
    - expense_tag: base tag for expense account (amount > 0).
    - income_tag: base tag for income account (amount < 0).
    - skip_duplicates: if True, skip rows whose ref is already stored.

    Returns the number of transactions created.
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if not header or not set(PARSED_HEADER).issubset(set(header)):
            raise ValueError(
                f"CSV must have columns {PARSED_HEADER}. Got: {header}"
            )

    created = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = datetime.strptime(row.get("date"), "%Y-%m-%d")
            description = row.get("description")
            ref = f"{bank_tag}-{row.get('ref')}"
            currency = row.get("currency")
            amount = Decimal(row.get("amount"))

            if skip_duplicates and ref is not None:
                existing = session.query(Transaction).filter(Transaction.external_reference == ref).first()
                if existing is not None:
                    continue

            bank = account_services.upsert_account(
                session, AccountType.ASSET, bank_tag
            )

            desc_display = f"{description}".strip()
            if len(desc_display) > 256:
                desc_display = desc_display[:253] + "..."

            if amount > 0:
                expense = account_services.upsert_account(
                    session, AccountType.EXPENSE, expense_tag
                )
                splits = [(bank.id, -amount), (expense.id, amount)]
            else:
                income = account_services.upsert_account(
                    session, AccountType.INCOME, income_tag
                )
                splits = [(bank.id, -amount), (income.id, amount)]

            transaction_services.create_transaction(
                session,
                desc_display,
                splits,
                timestamp=ts,
                external_reference=ref,
                currency=currency,
            )
            created += 1

    return created


def main() -> None:
    """CLI: load parsed CSVs from directory subdirs into the ledger."""

    import argparse
    import sys

    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from accounting.db import get_session, init_db

    parser = argparse.ArgumentParser(
        description="Load parsed statement CSVs (from parsers.parse) into the ledger"
    )
    parser.add_argument(
        "dir",
        type=Path,
        nargs="?",
        default=Path("parsers/out/post"),
        help="Directory with subdirs (default: parsers/out/post). Each subdir/*.csv uses bank=subdir",
    )
    parser.add_argument(
        "--expense",
        default="uncategorized",
        help="Expense account tag for outflows (default: uncategorized)",
    )
    parser.add_argument(
        "--income",
        default="uncategorized",
        help="Income account tag for inflows (default: uncategorized)",
    )
    parser.add_argument(
        "--no-skip-dup",
        action="store_true",
        help="Do not skip duplicate rows",
    )
    args = parser.parse_args()

    root = args.dir.resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    subdirs = sorted(d for d in root.iterdir() if d.is_dir())
    if not subdirs:
        print("No subdirectories found.", file=sys.stderr)
        sys.exit(1)

    init_db()
    session = get_session()
    try:
        total = 0
        for subdir in subdirs:
            bank_tag = subdir.name
            csv_paths = sorted(subdir.glob("*.csv"))
            for csv_path in csv_paths:
                n = load_parsed_csv(
                    csv_path,
                    session,
                    bank_tag=bank_tag,
                    expense_tag=args.expense,
                    income_tag=args.income,
                    skip_duplicates=not args.no_skip_dup,
                )
                total += n
                print(f"{bank_tag}/{csv_path.name}: {n} transaction(s)")
        session.commit()
        print(f"Total: {total} transaction(s) loaded.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
