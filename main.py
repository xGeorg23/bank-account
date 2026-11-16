from exception.bank_exception import AccountClosedError, AccountFrozenError, InvalidOperationError, \
    InsufficientFundsError
from model.bank_account import BankAccount
from model.investment_account import InvestmentAccount
from model.premium_account import PremiumAccount
from model.savings_account import SavingsAccount
from model.user import User
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


def test_bank_account_one():
    try:
        user = User(1, "Иван Иванович Иванов", 33)
        account = BankAccount(None, user, 5000, StatusAccount.ACTIVE, CurrencyType.USD, AccountType.DEBIT)
        account.deposit(500)
        print(account.__str__())
        print("\n")
        account.withdraw(5600)
        print(account.__str__())
        print("\n")
    except AccountClosedError as e :
        print(e)
    except AccountFrozenError as e :
        print(e)
    except InvalidOperationError as e :
        print(e)
    except InsufficientFundsError as e :
        print(e)

def test_bank_account_two():
    try:
        user = User(1, "Иван Иванович Иванов", 33)
        account = BankAccount("1234 0988 6447 3345", user, 0, StatusAccount.FROZEN, CurrencyType.USD, AccountType.CURRENCY)
        print(account.__str__())
        account.deposit(500)
    except AccountClosedError as e :
        print(e)
    except AccountFrozenError as e :
        print(e)
    except InvalidOperationError as e :
       print("error: Сумма пополнения указана некоректно")

def test_savings_account():
    try:
        user = User(1, "Иван Иванович Иванов", 33)
        account = SavingsAccount(None, user, 50000, StatusAccount.ACTIVE, CurrencyType.USD, AccountType.SAVINGS, 10000, 10.2)
        account.deposit(500)
        print(account.__str__())
        print("\n")

        account.apply_monthly_interest()
        print(account.__str__())
        print("\n")

        account.withdraw(40000)
        print(account.__str__())
        print("\n")

        account.apply_monthly_interest()
        print(account.__str__())
        print("\n")
    except AccountClosedError as e :
        print(e)
    except AccountFrozenError as e :
        print(e)
    except InvalidOperationError as e :
        print(e)
    except InsufficientFundsError as e :
        print(e)

def test_premium_account():
    try:
        user = User(1, "Иван Иванович Иванов", 33)
        account = PremiumAccount(None, user, 5000000, StatusAccount.ACTIVE, CurrencyType.USD,
                                 AccountType.PREMIUM, 1000000, 1000, 4000000)
        account.deposit(500)
        print(account.__str__())
        print("\n")

        account.withdraw(4000000)
        print(account.__str__())
        print("\n")

        account.withdraw(1000000)
        print(account.__str__())
        print("\n")

    except AccountClosedError as e:
        print(e)
    except AccountFrozenError as e :
        print(e)
    except InvalidOperationError as e :
        print(e)
    except InsufficientFundsError as e :
        print(e)

def test_investment_account():
    try:
        investment_active = {"stocks" : 0, "bonds" : 0, "etf" : 0}
        user = User(1, "Иван Иванович Иванов", 33)
        account = InvestmentAccount(None, user, 5000, StatusAccount.ACTIVE, CurrencyType.USD,
                                 AccountType.INVESTMENT, investment_active)
        # account.deposit(500)
        print(account.__str__())
        print("\n")

        growth_rates = {"stocks" : 7, "bonds" : 4, "etf" : 10}
        print(account.project_yearly_growth(growth_rates))
        print("\n")

        account.withdraw(1200)
        print(account.__str__())
        print("\n")


    except AccountClosedError as e:
        print(e)
    except AccountFrozenError as e :
        print(e)
    except InvalidOperationError as e :
        print(e)
    except InsufficientFundsError as e :
        print(e)

# test_bank_account_one()
# test_bank_account_two()
# test_savings_account()
# test_premium_account()
test_investment_account()