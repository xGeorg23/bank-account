from datetime import datetime

from exception.bank_exception import AccountClosedError, AccountFrozenError, InvalidOperationError, \
    InsufficientFundsError, NotFoundError, NightOperationError
from bank.bank import Bank
from bank.account.bank_account import BankAccount
from bank.account.investment_account import InvestmentAccount
from bank.account.premium_account import PremiumAccount
from bank.account.savings_account import SavingsAccount
from bank.client import Client
from bank.transaction.transaction import Transaction
from bank.transaction.transaction_processor import TransactionProcessor
from bank.transaction.transaction_queue import TransactionQueue
from bank.audit.audit_log import AuditLog
from bank.audit.audit_report import AuditReport
from bank.audit.risk_analyzer import RiskAnalyzer
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount
from util.transaction_type import TransactionType


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
    try: 
        client = Client(1, "Иванов Иван Иванович", [], ["+79555555555"], 19, "123", 1)
        client1 = Client(2, "Да Да Да", [], ["+79333333333"], 100, "321", 3)
        bank = Bank([])


        bank.add_client(client)
        bank.add_client(client1)

        bank.authenticate_client(client.id())
        # bank.authenticate_client(client.id())

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
        print("рейтинг клиентов: ")
        for ranked_client in bank.get_clients_ranking(): 
            print(f"{ranked_client.__str__()}")

    except AccountClosedError as e: 
        print(e)
    except AccountFrozenError as e : 
        print(e)
    except NightOperationError as e : 
        print(e)
    except InsufficientFundsError as e : 
        print(e)
    except NotFoundError as e : 
        print(e)

def test_transaction():
    try:
        bank = Bank([])
        client = Client(1, "Иванов Иван Иванович", [], ["+79555555555"], 19, "123", 1)
        client_1 = Client(2, "Да Да Да", [], ["+79333333333"], 100, "321", 3)

        bank.add_client(client)
        bank.add_client(client_1)

        bank.open_account(client.id(), "1230999", AccountType.DEBIT, CurrencyType.RUB)
        bank.open_account(client.id(), "9990321", AccountType.SAVINGS, CurrencyType.RUB)
        bank.open_account(client_1.id(), "1357986", AccountType.PREMIUM, CurrencyType.RUB)
        bank.open_account(client_1.id(), "2468097", AccountType.CURRENCY, CurrencyType.EUR)

        bank.deposit(client.id(), "1230999", 100000)
        bank.deposit(client.id(), "9990321", 500000)
        bank.deposit(client_1.id(), "1357986", 100000)
        bank.deposit(client_1.id(), "2468097", 200000)

        account_debit = bank.search_accounts(client.id(), "1230999")
        account_saving = bank.search_accounts(client.id(), "9990321")
        account_premium = bank.search_accounts(client_1.id(), "1357986")
        account_currency = bank.search_accounts(client_1.id(), "2468097")

        print("Балансы ДО обработки:")
        print(f"  debit: {account_debit.balance()} | saving: {account_saving.balance()}")
        print(f"  premium: {account_premium.balance()} | currency: {account_currency.balance()}")
        print()

        transaction_1 = Transaction(1, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 1000, account_debit, account_saving)
        transaction_2 = Transaction(2, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 2000, account_debit, account_premium)
        transaction_3 = Transaction(3, TransactionType.TRANSFER_EXTERNAL, CurrencyType.RUB, 3000, account_debit, account_currency)

        transaction_4 = Transaction(4, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 4000, account_saving, account_debit)
        transaction_5 = Transaction(5, TransactionType.TRANSFER_EXTERNAL, CurrencyType.RUB, 5000, account_saving, account_premium)
        transaction_6 = Transaction(6, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 6000, account_saving, account_currency)

        transaction_7 = Transaction(7, TransactionType.TRANSFER_EXTERNAL, CurrencyType.RUB, 7000, account_premium, account_debit)
        transaction_8 = Transaction(8, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 8000, account_premium, account_currency)
        transaction_9 = Transaction(9, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 9000, account_premium, account_saving)

        transaction_10 = Transaction(10, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 10000, account_currency, account_debit)

        transaction_queue = TransactionQueue()
        transaction_queue.add(transaction_1)
        transaction_queue.add(transaction_2)
        transaction_queue.add(transaction_3)
        transaction_queue.add(transaction_4)
        transaction_queue.add(transaction_5)
        transaction_queue.add(transaction_6)
        transaction_queue.add(transaction_7)
        transaction_queue.add(transaction_8)
        transaction_queue.add(transaction_9)
        transaction_queue.add(transaction_10)
        transaction_queue.cancel(8)

        print("Очередь ДО обработки:")
        print(transaction_queue.__str__())
        transaction_queue.deferred_transactions(7, datetime(2026, 11, 21, 20, 0))
        print()

        processor = TransactionProcessor(transaction_queue)
        processor.run()

        print("Очередь ПОСЛЕ обработки:")
        print(transaction_queue.__str__())
        print()
        print("Балансы ПОСЛЕ обработки:")
        print(f"  debit: {account_debit.balance()} | saving: {account_saving.balance()}")
        print(f"  premium: {account_premium.balance()} | currency: {account_currency.balance()}")
        print()
        print("Журнал ошибок:")
        processor.print_error_log()

    except AccountClosedError as e:
        print(e)
    except AccountFrozenError as e :
        print(e)
    except NightOperationError as e :
        print(e)
    except InsufficientFundsError as e :
        print(e)
    except NotFoundError as e :
        print(e)


def test_audit():
    bank = Bank([])
    client = Client(1, "Иванов Иван Иванович", [], ["+79555555555"], 19, "123", 1)
    bank.add_client(client)

    bank.open_account(client.id(), "1111001", AccountType.DEBIT, CurrencyType.RUB)
    bank.open_account(client.id(), "1111002", AccountType.DEBIT, CurrencyType.RUB)
    bank.open_account(client.id(), "1111003", AccountType.DEBIT, CurrencyType.RUB)
    bank.deposit(client.id(), "1111001", 300000)

    acc_a = bank.search_accounts(client.id(), "1111001")
    acc_b = bank.search_accounts(client.id(), "1111002")
    acc_c = bank.search_accounts(client.id(), "1111003")

    audit_log = AuditLog()
    analyzer = RiskAnalyzer(audit_log)
    queue = TransactionQueue()
    processor = TransactionProcessor(queue, audit_log, analyzer)
    report = AuditReport(audit_log)

    queue.add(Transaction(1, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 1000, acc_a, acc_b))
    queue.add(Transaction(2, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 2000, acc_a, acc_b))
    queue.add(Transaction(3, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 3000, acc_a, acc_b))
    queue.add(Transaction(4, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 4000, acc_a, acc_c))
    queue.add(Transaction(5, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 150000, acc_a, acc_c))
    queue.add(Transaction(6, TransactionType.TRANSFER_INTERNAL, CurrencyType.RUB, 999999999, acc_b, acc_a))

    print("Очередь перед обработки")
    print(queue.__str__())
    print()

    processor.run()
    print("Очередь после обработки")
    print(queue.__str__())
    print()
    print(report.suspicious_operations())
    print()
    for account in client.list_bank_account():
        print(report.client_risk_profile(client.full_name(), account.get_account_number()))
    print()
    print(report.error_statistics())
    print()
    print(f"Баланс acc_a: {acc_a.balance()}")


# test_bank_account_one()
# test_bank_account_two()
# test_savings_account()
# test_premium_account()
# test_investment_account()
# test_bank()
# test_transaction()
test_audit()