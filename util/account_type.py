from enum import Enum


class AccountType(Enum):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
    DEPOSIT = 'DEPOSIT'
    CURRENCY = 'CURRENCY'
