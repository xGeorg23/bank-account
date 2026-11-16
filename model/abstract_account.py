from abc import ABC, abstractmethod

from util.status_account import StatusAccount


class AbstractAccount(ABC):
    account_number:str
    full_name:str
    __balance:float
    status_account:StatusAccount

    def __init__(self, account_number, full_name:str, balance:float, status_account:StatusAccount):
        self.account_number = account_number
        self.full_name = full_name
        self.__balance = balance
        self.status_account = status_account

    @abstractmethod
    def deposit(self, amount:float):
        self.__balance += amount

    @abstractmethod
    def withdraw(self, amount:float):
        self.__balance -= amount

    @abstractmethod
    def get_account_info(self):
        return (f"account_number = {self.account_number[-4:]}\n"
                f"user = {self.full_name}\n"
                f"status = {self.status_account.value}\n"
                f"balance = {self.__balance}")

    def balance(self) -> float:
        return self.__balance

    def account_number(self) -> str:
        return self.account_number