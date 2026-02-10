"""
Load parsed statement CSVs into the ledger.

Expects CSVs produced by parsers.parse (columns: date, description, ref, currency, amount).
Each row becomes one transaction: credit bank asset, debit expense.
"""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from accounting.models import AccountType, Transaction, create_transaction
from accounting.rest_api.accounts import services as account_services


# Parsed CSV columns (must match parsers.parse.PARSED_HEADER)
PARSED_HEADER = ["date", "description", "ref", "currency", "amount"]


def load_parsed_csv(
    csv_path: Path | str,
    session: Session,
    *,
    bank_tag: str = "unspecified",
    expense_tag: str = "uncategorized",
    skip_duplicates: bool = True,
) -> int:
    """
    Load a parsed statement CSV into the ledger.

    - csv_path: path to a parsed CSV (columns: date, description, ref, currency, amount).
    - session: SQLAlchemy session (caller commits).
    - bank_tag: base tag for the asset account -> asset:{bank_tag}:{currency}.
    - expense_tag: base tag for the expense account -> expense:{expense_tag}:{currency}.
    - skip_duplicates: if True, skip rows whose ref is already stored as ext_ref on an existing transaction.

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
            ref = row.get("ref").strip()
            currency = row.get("currency")
            amount = Decimal(row.get("amount"))

            if skip_duplicates and ref is not None:
                existing = session.query(Transaction).filter(Transaction.ext_ref == ref).first()
                if existing is not None:
                    continue

            bank = account_services.get_or_create_account(
                session, AccountType.ASSET, f"{bank_tag}:{currency}"
            )
            expense = account_services.get_or_create_account(
                session, AccountType.EXPENSE, f"{expense_tag}:{currency}"
            )

            desc_display = f"{description}".strip()
            if len(desc_display) > 256:
                desc_display = desc_display[:253] + "..."

            create_transaction(
                session,
                desc_display,
                [(bank.id, -amount), (expense.id, amount)],
                timestamp=ts,
                ext_ref=ref,
            )
            created += 1

    return created


def main() -> None:
    """CLI: load one or more parsed CSVs into the ledger."""
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
        "csv_paths",
        type=Path,
        help="Parsed CSV file(s)",
    )
    parser.add_argument(
        "--bank",
        default="unspecified",
        help="Bank account base tag (default: unspecified)",
    )
    parser.add_argument(
        "--expense",
        default="uncategorized",
        help="Expense account base tag (default: uncategorized)",
    )
    parser.add_argument(
        "--no-skip-dup",
        action="store_true",
        help="Do not skip duplicate (date, description, amount) rows",
    )
    args = parser.parse_args()

    csv_paths = sorted(args.csv_paths.parent.glob(args.csv_paths.name))
    if not csv_paths:
        print("No CSV files found.", file=sys.stderr)
        sys.exit(1)

    init_db()
    session = get_session()
    try:
        total = 0
        for csv_path in csv_paths:
            n = load_parsed_csv(
                csv_path,
                session,
                bank_tag=args.bank,
                expense_tag=args.expense,
                skip_duplicates=not args.no_skip_dup,
            )
            total += n
            print(f"{csv_path.name}: {n} transaction(s)")
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
