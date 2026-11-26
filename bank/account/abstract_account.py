from abc import ABC, abstractmethod
from datetime import datetime

from exception.bank_exception import InvalidOperationError
from util.status_account import StatusAccount


class AbstractAccount(ABC): 
    account_number: str
    full_name: str
    __balance: float
    status_account: StatusAccount

    def __init__(self, account_number, full_name: str, balance: float, status_account: StatusAccount):
        if balance < 0:
            raise InvalidOperationError("Баланс не может быть отрицательным")

        self.account_number = account_number
        self.full_name = full_name
        self.__balance = balance
        self.status_account = status_account
        self.created_at = datetime.now()

    @abstractmethod
    def deposit(self, amount: float):
        self.__balance += amount

    @abstractmethod
    def withdraw(self, amount: float):
        self.__balance -= amount

    @abstractmethod
    def get_account_info(self):

        return (f"account_number = {self.account_number[-4: ]}\n"
                f"user = {self.full_name}\n"
                f"status = {self.status_account.value}\n"
                f"balance = {self.__balance}")

    def balance(self) -> float: 
        return self.__balance

    def get_account_number(self) -> str:
        return self.account_number

    def get_status_account(self) -> StatusAccount:
        return self.status_account