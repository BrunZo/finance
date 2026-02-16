"""Reports services: expense aggregates and other report data."""

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from accounting.models import Account, AccountType, Split, Transaction


def _enum_value(x) -> str:
    return x.value if hasattr(x, "value") else str(x)


def get_expenses_df(session: Session) -> pd.DataFrame:
    query = (
        session.query(
            Split.amount,
            Account.account_type,
            Account.tag,
            Transaction.currency,
            Transaction.timestamp.label("date"),
            Transaction.description,
        )
        .join(Account, Split.account_id == Account.id)
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(Account.account_type == AccountType.EXPENSE)
    )
    df = pd.read_sql(query.statement, session.bind)
    if df.empty:
        return pd.DataFrame(columns=["account_name", "currency", "amount"])
    df["account_type"] = df["account_type"].apply(_enum_value)
    df["account_name"] = df["account_type"] + ":" + df["tag"]
    df["currency"] = df["currency"].fillna("USD")
    return df.groupby(["account_name", "currency"], as_index=False)["amount"].sum()


def get_expenses_rows(session: Session) -> list[dict]:
    df = get_expenses_df(session)
    if df.empty:
        return []
    return [
        {"account_name": row["account_name"], "currency": row["currency"], "amount": float(row["amount"])}
        for _, row in df.iterrows()
    ]


def get_expenses_tree(session: Session) -> dict:
    """
    Build a hierarchical tree of expense accounts.
    Parent nodes (e.g. expense:subscriptions) aggregate their children (expense:subscriptions:cursor, etc.).
    """
    rows = get_expenses_rows(session)
    amounts_by_name: dict[str, dict[str, float]] = {}
    for row in rows:
        name = row["account_name"]
        curr = row["currency"]
        amt = float(row["amount"])
        if name not in amounts_by_name:
            amounts_by_name[name] = {}
        amounts_by_name[name][curr] = amounts_by_name[name].get(curr, 0) + amt

    _root: dict = {}

    def _ensure_path(tree: dict, path: list[str], direct_amounts: dict[str, float]) -> None:
        node = tree
        for i, segment in enumerate(path):
            prefix = ":".join(path[: i + 1])
            if segment not in node:
                node[segment] = {
                    "segment": segment,
                    "full_name": prefix,
                    "direct": {},
                    "children": {},
                }
            if i == len(path) - 1:
                for c, a in direct_amounts.items():
                    node[segment]["direct"][c] = node[segment]["direct"].get(c, 0) + a
            node = node[segment]["children"]

    for full_name, amounts in amounts_by_name.items():
        if not full_name.startswith("expense:"):
            continue
        path = full_name.split(":")
        _ensure_path(_root, path, amounts)

    def _to_node(segment: str, data: dict) -> dict:
        children = [_to_node(k, v) for k, v in sorted(data["children"].items())]
        total = dict(data["direct"])
        for c in children:
            for curr, amt in c["total_amounts_by_currency"].items():
                total[curr] = total.get(curr, 0) + amt
        return {
            "name": data["segment"],
            "full_name": data["full_name"],
            "direct_amounts_by_currency": data["direct"],
            "total_amounts_by_currency": total,
            "children": children,
        }

    if "expense" in _root:
        kids = _root["expense"]["children"]
        tree = [_to_node(k, v) for k, v in sorted(kids.items())]
    else:
        tree = []

    return {"children": tree}


def get_balances_by_currency(session: Session) -> list[dict]:
    """Return balance per (account, currency) for asset and liability accounts."""
    query = (
        session.query(
            Account.id.label("account_id"),
            Account.account_type,
            Account.tag,
            Transaction.currency,
            func.coalesce(func.sum(Split.amount), 0).label("balance"),
        )
        .join(Split, Split.account_id == Account.id)
        .join(Transaction, Split.transaction_id == Transaction.id)
        .filter(Account.account_type.in_([AccountType.ASSET, AccountType.LIABILITY]))
        .group_by(Account.id, Account.account_type, Account.tag, Transaction.currency)
    )
    rows = query.all()
    result = []
    for row in rows:
        balance = float(row.balance)
        if balance == 0:
            continue
        account_name = f"{row.account_type.value}:{row.tag}"
        currency = row.currency
        result.append(
            {
                "account_id": row.account_id,
                "account_name": account_name,
                "currency": currency,
                "balance": balance,
            }
        )
    return result
