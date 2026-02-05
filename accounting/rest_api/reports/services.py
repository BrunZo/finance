"""Reports services: expense aggregates and other report data."""

import pandas as pd
from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, Split, Transaction
from accounting.rest_api.reports.schemas import ExpenseRow


def _enum_value(x) -> str:
    return x.value if hasattr(x, "value") else str(x)


def get_expenses_df(session: Session) -> pd.DataFrame:
    query = (
        session.query(
            Split.amount,
            Account.account_type,
            Account.tag,
            Transaction.timestamp.label("date"),
            Transaction.description,
        )
        .join(Account, Split.account_id == Account.id)
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(Account.account_type == AccountType.EXPENSE)
    )
    df = pd.read_sql(query.statement, session.bind)
    if df.empty:
        return pd.DataFrame(columns=["account_name", "amount"])
    df["account_type"] = df["account_type"].apply(_enum_value)
    df["account_name"] = df["account_type"] + ":" + df["tag"]
    return df.groupby("account_name", as_index=False)["amount"].sum()


def get_expenses_rows(session: Session) -> list[ExpenseRow]:
    """Expense totals by account for the API."""
    df = get_expenses_df(session)
    if df.empty:
        return []
    return [
        ExpenseRow(account_name=row["account_name"], amount=float(row["amount"]))
        for _, row in df.iterrows()
    ]
