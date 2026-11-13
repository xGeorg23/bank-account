from abc import ABC, abstractmethod

from exception.bank_exception import InsufficientFundsError
from model.user import User
from util.status_account import StatusAccount


class AbstractAccount(ABC):
    account_number:str
    user:User
    __balance:float
    status_account:StatusAccount

    def __init__(self, account_number, user:User, balance:float, status_account:StatusAccount):
        self.account_number = account_number
        self.user = user
        self.__balance = balance
        self.status_account = status_account

    @abstractmethod
    def deposit(self, amount:float):
        self.__balance += amount

    @abstractmethod
    def withdraw(self, amount:float):
        if amount > self.__balance:
            raise InsufficientFundsError("сумма баланса меньше суммы списания")
        self.__balance -= amount

    @abstractmethod
    def get_account_info(self):
        return (f"account_number = {self.account_number[-4:]}\n"
                f"user = ({self.user.__str__()})\n"
                f"satus = {self.status_account.value}\n"
                f"balance = {self.__balance}")