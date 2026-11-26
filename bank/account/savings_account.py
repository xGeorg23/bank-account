from exception.bank_exception import InvalidOperationError
from bank.account.bank_account import BankAccount
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


class SavingsAccount(BankAccount): 
    min_balance: float
    savings_percentage: float

    def __init__(self, account_number, full_name: str, balance: float, status_account: StatusAccount,
                 currency_type: CurrencyType, account_type: AccountType, min_balance: float, savings_percentage: float): 

        super().__init__(account_number, full_name, balance, status_account, currency_type, account_type)
        self.min_balance = min_balance
        self.savings_percentage = savings_percentage

    def withdraw(self, amount: float): 
        if super().balance() - amount < self.min_balance: 
            raise InvalidOperationError("превышает минимальную сумму баланса")

        super().withdraw(amount)

    def get_account_info(self): 
        return f"{super().get_account_info()}\nmin_balance = {self.min_balance}\nsavings_percentage = {self.savings_percentage}"

    def __str__(self): 
        return self.get_account_info()

    def apply_monthly_interest(self):
        super().deposit(super().balance() * self.savings_percentage / 100)