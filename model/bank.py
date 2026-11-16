from datetime import datetime, time

from exception.bank_exception import NotFoundError, NightOperationError, BlockedError
from model.bank_account import BankAccount
from model.client import Client
from model.investment_account import InvestmentAccount
from model.premium_account import PremiumAccount
from model.savings_account import SavingsAccount
from util.account_type import AccountType
from util.currency import CurrencyType
from util.status_account import StatusAccount


class Bank:
    clients:list[Client]

    def __init__(self,clients:list[Client]):
        self.clients = clients

    def add_client(self, client:Client):
        self.clients.append(client)

    def open_account(self, client_id:int, account_number:str, account_type:AccountType, currency_type:CurrencyType):
        client = self.search_client(client_id)

        if account_type is AccountType.PREMIUM:
            account = PremiumAccount(account_number, client.full_name(), 0, StatusAccount.ACTIVE,
                                     currency_type, AccountType.PREMIUM, 100000, 2, 500000)
        elif account_type is AccountType.INVESTMENT:
            account = InvestmentAccount(account_number, client.full_name(), 0, StatusAccount.ACTIVE,
                                        currency_type, AccountType.INVESTMENT)
        elif account_type is AccountType.SAVINGS:
            account = SavingsAccount(account_number, client.full_name(), 0, StatusAccount.ACTIVE,
                                     currency_type, AccountType.SAVINGS, 0, 8)
        else:
            account = BankAccount(account_number, client.full_name(), 0, StatusAccount.ACTIVE, currency_type, account_type)

        client = self.search_client(client_id)
        client.list_bank_account().append(account)

    def close_account(self, client_id:int, account_number:str):
        client = self.search_client(client_id)
        account = self.search_accounts(client, account_number)
        account.status_account = StatusAccount.CLOSE

    def freeze_account(self, client_id:int, account_number:str):
        client = self.search_client(client_id)
        account = self.search_accounts(client, account_number)
        account.status_account = StatusAccount.FROZEN

    def unfreeze_account(self, client_id:int, account_number:str):
        client = self.search_client(client_id)
        account = self.search_accounts(client, account_number)
        account.status_account = StatusAccount.ACTIVE

    def authenticate_client(self, client_id:int):
        client = self.search_client(client_id)
        if not client.get_suspiciously():
            try_write_password = 0
            while try_write_password <= 3:
                if try_write_password < 3:
                    write_password = input("напишите пароль:")
                    if write_password != client.password():
                        try_write_password += 1
                    else:
                        print("вход выполнен")
                        break
                else:
                    client.set_suspiciously(True)
                    print("Блокировка аккаунта")
                    break
        else:
            raise BlockedError("аккаунт заблокирован")

    def search_accounts(self, client:Client, account_number:str):
        bank_account = None
        for account in client.list_bank_account():
            if account.account_number == account_number:
                bank_account = account

        if bank_account is None:
            raise NotFoundError(f"Не найден счет с номером {account_number[-4:]}")

        return bank_account

    def search_client(self, client_id:int):
        client_bank = None
        for client in self.clients:
            if client.id() == client_id:
                client_bank = client

        if client_bank is None:
            raise NotFoundError(f"Не найден пользователь с id {client_id}")

        return client_bank

    def get_total_balance(self, client_id:int):
        client = self.search_client(client_id)
        totals = 0
        for account in client.list_bank_account():
            totals += account.balance()
        return totals

    def get_clients_ranking(self) -> list[Client]:
        return sorted(self.clients, key=lambda client: client.ranking())

    def withdraw(self, client_id:int, account_number:str, amount:int):
        client = self.search_client(client_id)
        account = self.search_accounts(client, account_number)
        if time(0, 0) < datetime.now().time() < time(5, 0):
            raise NightOperationError("Операции запрещены с 00:00 до 05:00")
        account.withdraw(amount)

    def deposit(self, client_id:int, account_number:str, amount:int):
        client = self.search_client(client_id)
        account = self.search_accounts(client, account_number)
        if time(0, 0) < datetime.now().time() < time(5, 0):
            client.set_suspiciously(True)
            raise NightOperationError("Операции запрещены с 00:00 до 05:00")
        account.deposit(amount)