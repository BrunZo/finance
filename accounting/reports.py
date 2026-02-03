"""Pandas-based reports for the ledger."""

import pandas as pd
from sqlalchemy.orm import Session

from accounting.models import AccountType, Split, Account, Transaction


def _enum_value(x):
    """Normalize enum to string for DataFrame handling."""
    return x.value if hasattr(x, "value") else x


def get_cleaned_expenses(session: Session) -> pd.DataFrame:
    """
    Return a DataFrame of expense totals by account (account_type:tag).
    Only includes splits in Expense accounts; bank and reimbursement movements are excluded.
    """
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
    expenses = pd.read_sql(query.statement, session.bind)
    if expenses.empty:
        return pd.DataFrame(columns=["account_name", "amount"])

    expenses["account_type"] = expenses["account_type"].apply(_enum_value)
    expenses["account_name"] = expenses["account_type"] + ":" + expenses["tag"]
    report = expenses.groupby("account_name", as_index=False)["amount"].sum()
    return report
