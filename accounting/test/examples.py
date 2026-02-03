from decimal import Decimal
from typing import List
from accounting.models import AccountType, create_transaction
from accounting.test.helpers import get_account_id


def salary_income(session, amount: Decimal):
    bank = get_account_id(session, AccountType.ASSET, "bank")
    income_all = get_account_id(session, AccountType.INCOME, "all")
    create_transaction(
        session,
        "Salary",
        [
            (bank, amount),
            (income_all, -amount),
        ],
    )
    session.commit()


def rent_payment(session, amount: Decimal):
    bank = get_account_id(session, AccountType.ASSET, "bank")
    expense_all = get_account_id(session, AccountType.EXPENSE, "all")
    create_transaction(
        session,
        "Rent payment",
        [
            (bank, -amount),
            (expense_all, amount),
        ],
    )
    session.commit()


def split_dinner(session, shares: List[Decimal]):
    bank = get_account_id(session, AccountType.ASSET, "bank")
    reimbursements = get_account_id(session, AccountType.ASSET, "reimbursements")
    dining = get_account_id(session, AccountType.EXPENSE, "dining")

    total_amount = sum(shares)
    total_reimbursements = sum(shares[1:])
    create_transaction(
        session,
        "Dinner with friends",
        [
            (bank, -total_amount),
            (dining, shares[0]),
            (reimbursements, total_reimbursements),
        ],
    )
    session.commit()


def friend_reimbursement(session, amount: Decimal):
    bank = get_account_id(session, AccountType.ASSET, "bank")
    reimbursements = get_account_id(session, AccountType.ASSET, "reimbursements")
    create_transaction(
        session,
        "Reimbursement",
        [
            (bank, amount),
            (reimbursements, -amount),
        ],
    )
    session.commit()
