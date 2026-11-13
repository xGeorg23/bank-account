from exception.bank_exception import AccountClosedError, AccountFrozenError, InvalidOperationError, \
    InsufficientFundsError
from model.bank_account import BankAccount
from model.user import User
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


def test_one():
    try:
        user = User(1, "Иван Иванович Иванов", 33)
        account = BankAccount(None, user, 5000, StatusAccount.ACTIVE, CurrencyType.USD, AccountType.DEBIT)
        account.deposit(500)
        print(account.__str__())
        print("\n")
        account.withdraw(5600)
        print(account.__str__())
        print("\n")
    except AccountClosedError:
        print("error: Аккаунт закрыт")
    except AccountFrozenError:
        print("error: Аккаунт заморожен")
    except InvalidOperationError:
        print("error: Сумма указаана некоректно")
    except InsufficientFundsError:
        print("error: сумма баланса меньше суммы списания")

def test_two():
    try:
        user = User(1, "Иван Иванович Иванов", 33)
        account = BankAccount("1234 0988 6447 3345", user, 0, StatusAccount.FROZEN, CurrencyType.USD, AccountType.CURRENCY)
        print(account.__str__())
        account.deposit(500)
    except AccountClosedError:
        print("error: Аккаунт закрыт")
    except AccountFrozenError:
        print("error: Аккаунт заморожен")
    except InvalidOperationError:
       print("error: Сумма пополнения указаана некоректно")


test_one()
# test_two()