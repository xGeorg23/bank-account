from exception.bank_exception import AccountClosedError, AccountFrozenError, InvalidOperationError, \
    InsufficientFundsError, NotFoundError
from model.bank import Bank
from model.bank_account import BankAccount
from model.investment_account import InvestmentAccount
from model.premium_account import PremiumAccount
from model.savings_account import SavingsAccount
from model.client import Client
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


def test_bank_account_one():
    try:
        account = BankAccount(None, "Иван Иванович Иванов", 5000, StatusAccount.ACTIVE, CurrencyType.USD, AccountType.DEBIT)
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
        account = BankAccount("1234 0988 6447 3345", "Иван Иванович Иванов", 0, StatusAccount.FROZEN, CurrencyType.USD, AccountType.CURRENCY)
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
        account = SavingsAccount(None, "Иван Иванович Иванов", 50000, StatusAccount.ACTIVE, CurrencyType.USD, AccountType.SAVINGS, 10000, 10.2)
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
        account = PremiumAccount(None, "Иван Иванович Иванов", 5000000, StatusAccount.ACTIVE, CurrencyType.USD,
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
        account = InvestmentAccount(None, "Иван Иванович Иванов", 5000, StatusAccount.ACTIVE, CurrencyType.USD,
                                 AccountType.INVESTMENT)
        account.deposit(500)
        print(account.__str__())
        print("\n")

        growth_rates = {"stocks" : 7, "bonds" : 4, "etfs" : 10}
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
    except NotFoundError as e:
        print(e)

def test_bank():
    client = Client(1, "Иванов Иван Иванович", [], ["+79555555555"], 19, "1qaswe", 1)
    client1 = Client(2, "Да Да Да", [], ["+79333333333"], 100, "12321", 3)
    bank = Bank([])

    bank.add_client(client)
    bank.add_client(client1)

    bank.authenticate_client(client.id())
    bank.authenticate_client(client.id())

    bank.open_account(client.id(), "1230999", AccountType.DEBIT, CurrencyType.RUB)
    bank.open_account(client.id(), "9990321", AccountType.SAVINGS, CurrencyType.RUB)
    bank.open_account(client1.id(), "1357986", AccountType.PREMIUM, CurrencyType.RUB)
    bank.open_account(client1.id(), "2468097", AccountType.INVESTMENT, CurrencyType.RUB)

    bank.deposit(client.id(), "1230999", 10000)
    bank.deposit(client.id(), "9990321", 50000)
    bank.deposit(client1.id(), "1357986", 100000)
    bank.deposit(client1.id(), "2468097", 200000)
    bank.withdraw(client.id(), "1230999", 3000)

    print(f"баланс {client.full_name()}: {bank.get_total_balance(client.id())}")
    print(f"баланс {client1.full_name()}: {bank.get_total_balance(client1.id())}")
    print("\n")
    print("рейтинг клиентов:")
    for ranked_client in bank.get_clients_ranking():
        print(f"{ranked_client.__str__()}")

# test_bank_account_one()
# test_bank_account_two()
# test_savings_account()
# test_premium_account()
# test_investment_account()
test_bank()