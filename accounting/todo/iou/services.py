


def _receivable_tag(friend_name: str | None) -> str:
    if not (friend_name and friend_name):
        return "receivables"
    return f"receivables:{friend_name}"


def _payable_tag(friend_name: str | None) -> str:
    if not (friend_name and friend_name):
        return "payables"
    return f"payables:{friend_name}"



def get_or_create_receivable_account(
    session: Session,
    friend_name: str | None = None,
) -> int:
    tag = _receivable_tag(friend_name)
    acc = account_services.get_or_create_account(session, AccountType.ASSET, tag)
    return acc.id


def get_or_create_payable_account(
    session: Session,
    friend_name: str | None = None,
) -> int:
    tag = _payable_tag(friend_name)
    acc = account_services.get_or_create_account(session, AccountType.LIABILITY, tag)
    return acc.id
