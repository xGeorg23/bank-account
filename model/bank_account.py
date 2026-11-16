import shortuuid

from exception.bank_exception import InvalidOperationError, AccountClosedError, AccountFrozenError, InsufficientFundsError
from model.abstract_account import AbstractAccount
from model.user import User
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


class BankAccount(AbstractAccount):
    currency_type:CurrencyType
    account_type:AccountType

    def __init__(self, account_number, user: User, balance: float, status_account: StatusAccount, currency_type: CurrencyType, account_type:AccountType):
        if account_number is None:
            account_number = shortuuid.uuid()

        super().__init__(account_number, user, balance, status_account)
        self.currency_type = currency_type
        self.account_type = account_type

    def deposit(self, amount:float):
        self.validate(amount)
        super().deposit(amount)

    def withdraw(self, amount:float):
        if amount > self.balance():
            raise InsufficientFundsError("сумма баланса меньше суммы списания")

        self.validate(amount)
        super().withdraw(amount)

    def get_account_info(self):
        return f"accountType = {self.account_type.value}\n{super().get_account_info()} {self.currency_type.value}"


    def __str__(self):
        return self.get_account_info()

    def validate(self, amount:float):
        if self.status_account == StatusAccount.CLOSE:
            raise AccountClosedError("Аккаунт закрыт")
        elif self.status_account == StatusAccount.FROZEN:
            raise AccountFrozenError("Аккаунт заморожен")
        elif amount <= 0:
            raise InvalidOperationError("Сумма указана некоректно")