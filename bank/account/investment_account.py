from exception.bank_exception import NotFoundError
from bank.account.bank_account import BankAccount
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


class InvestmentAccount(BankAccount): 
    investment_active: dict[str, int]

    def __init__(self, account_number, full_name: str, balance: float, status_account: StatusAccount,
                 currency_type: CurrencyType, account_type: AccountType): 

        super().__init__(account_number, full_name, balance, status_account, currency_type, account_type)
        self.investment_active = {"stocks": 0, "bonds": 0, "etf": 0}
        self.update_active(balance)

    def deposit(self, amount: float): 
        super().deposit(amount)
        self.update_active(amount)

    def withdraw(self, amount: float): 
        super().withdraw(amount)
        self.investment_active["stocks"] -= amount * (50 / 100)
        self.investment_active["bonds"] -= amount * (30 / 100)
        self.investment_active["etf"] -= amount * (20 / 100)

    def get_account_info(self): 
        return (f"{super().get_account_info()}\n"
                f"investment_active = {self.investment_active}")

    def __str__(self): 
        return self.get_account_info()

    def project_yearly_growth(self, growth_rates): 
        for key in growth_rates: 
            if key not in self.investment_active: 
                raise NotFoundError(f"Недоступный актив {key}")

        return ((self.investment_active["stocks"] * (growth_rates["stocks"] / 100)) +
                (self.investment_active["bonds"] * (growth_rates["bonds"] / 100)) +
                (self.investment_active["etf"] * (growth_rates["etf"] / 100)))

    def update_active(self, amount: float): 
        self.investment_active["stocks"] += amount * (50 / 100)
        self.investment_active["bonds"] += amount * (30 / 100)
        self.investment_active["etf"] += amount * (20 / 100)