from exception.bank_exception import InsufficientFundsError
from model.bank_account import BankAccount
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


class PremiumAccount(BankAccount):
    overdraft:float
    commission:float
    increased_limits:float

    def __init__(self, account_number, full_name: str, balance: float, status_account: StatusAccount, currency_type: CurrencyType,
                 account_type:AccountType, overdraft: float, commission: float, increased_limits: float):

        super().__init__(account_number, full_name, balance, status_account, currency_type, account_type)
        self.overdraft = overdraft
        self.commission = commission
        self.increased_limits = increased_limits


    def withdraw(self, amount:float):
        if self.increased_limits < amount:
            raise InsufficientFundsError("сумма списания превышает лимит")
        elif self.overdraft + self.balance() < (amount + self.commission):
            raise InsufficientFundsError("сумма списания превышает overdraft")

        super().validate(amount)
        super(BankAccount, self).withdraw(amount + self.commission)

    def get_account_info(self):
        return (f"{super().get_account_info()}\n"
                f"overdraft = {self.overdraft}\n"
                f"commission = {self.commission}\n"
                f"increased_limits = {self.increased_limits}\n")

    def __str__(self):
        return self.get_account_info()