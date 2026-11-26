from datetime import datetime

from bank.account.bank_account import BankAccount
from util.currency import CurrencyType
from util.transaction_status import TransactionStatus
from util.transaction_type import TransactionType


class Transaction: 
    __id: int
    __transaction_type: TransactionType
    __currency_type: CurrencyType
    __amount: float
    __sender: BankAccount
    __receiver: BankAccount
    __commission: float
    __priority: int
    __status: TransactionStatus
    __failure_reason: str
    __created_at: datetime
    __completed_at: datetime
    __deferred_at: datetime


    def __init__(self, id: int, transaction_type: TransactionType, currency_type: CurrencyType, amount: float,
                 sender: BankAccount, receiver: BankAccount):
        self.__id = id
        self.__transaction_type = transaction_type
        self.__currency_type = currency_type
        self.__amount = amount
        self.__sender = sender
        self.__commission = 0
        self.__priority = 0
        self.__receiver = receiver
        self.__status = TransactionStatus.PENDING
        self.__failure_reason = ""
        self.__created_at = datetime.now()
        self.__completed_at = None
        self.__deferred_at = None

    def get_id(self) -> int:
        return self.__id

    def get_sender(self) -> BankAccount:
        return self.__sender

    def get_receiver(self) -> BankAccount:
        return self.__receiver

    def get_status(self) -> TransactionStatus:
        return self.__status

    def set_status(self, status: TransactionStatus):
        self.__status = status

    def set_commission(self, commission: float):
        self.__commission = commission

    def set_completed_at(self, completed_at: datetime):
        self.__completed_at = completed_at

    def get_deferred_at(self) -> datetime:
        return self.__deferred_at

    def set_deferred_at(self, deferred_at: datetime):
        self.__deferred_at = deferred_at

    def get_priority(self) -> int:
        return self.__priority

    def set_priority(self, priority: int):
        self.__priority = priority

    def get_amount(self) -> float:
        return self.__amount

    def get_transaction_type(self) -> TransactionType:
        return self.__transaction_type

    def get_currency_type(self) -> CurrencyType:
        return self.__currency_type

    def get_failure_reason(self) -> str:
        return self.__failure_reason

    def set_failure_reason(self, failure_reason: str):
        self.__failure_reason = failure_reason

    def __str__(self):
        result = (f"Transaction(id = {self.__id}, type = {self.__transaction_type.value}, "
                  f"amount = {self.__amount} {self.__currency_type.value}, "
                  f"status = {self.__status.value}, commission = {self.__commission}, "
                  f"priority = {self.__priority})")

        if self.__failure_reason:
            result += f", причина отказа = {self.__failure_reason}"

        return result