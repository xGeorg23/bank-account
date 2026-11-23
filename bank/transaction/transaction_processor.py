from datetime import datetime

from bank.account.premium_account import PremiumAccount
from bank.audit.audit_log import AuditLog
from bank.audit.risk_analyzer import RiskAnalyzer
from bank.transaction.transaction import Transaction
from bank.transaction.transaction_queue import TransactionQueue
from exception.bank_exception import (
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
    InvalidOperationError, TransactionError, )
from util.audit_level import AuditLevel
from util.risk_level import RiskLevel
from util.status_account import StatusAccount
from util.transaction_status import TransactionStatus
from util.transaction_type import TransactionType


class TransactionProcessor:

    __transaction_queue: TransactionQueue
    __attempts: dict
    __error_log: list
    __audit_log: AuditLog
    __risk_analyzer: RiskAnalyzer

    MAX_ATTEMPTS = 3
    EXTERNAL_COMMISSION_RATE = 0.10
    EXCHANGE_RATES = {
        ("USD", "RUB"): 95.0,
        ("EUR", "RUB"): 100.0,
        ("USD", "EUR"): 0.95,
    }

    def __init__(self, transaction_queue: TransactionQueue,
                 audit_log: AuditLog, risk_analyzer: RiskAnalyzer):
        self.__transaction_queue = transaction_queue
        self.__audit_log = audit_log
        self.__risk_analyzer = risk_analyzer
        self.__attempts = {}
        self.__error_log = []

    def run(self):
        for transaction in list(self.__transaction_queue.get_transactions()):
            deferred = transaction.get_deferred_at()
            if deferred is not None and datetime.now() < deferred:
                continue
            self.process(transaction)

    def process(self, transaction: Transaction):
        audit_level: AuditLevel
        message: str = ""
        try:
            self.validate(transaction)
            commission = self.commission(transaction)
            received = self.convert_amount(transaction)
            level, error_message = next(iter(self.__risk_analyzer.analyze(transaction).items()))

            if level == RiskLevel.HIGH:
                self.__audit_log.record(AuditLevel.CRITICAL, "transfer_blocked", transaction.get_sender().full_name,
                                        transaction.get_sender().get_account_number(), "; ".join(error_message))
                self.fail(transaction, f"Операция заблокирована: {'; '.join(error_message)}")
                return
            self.execute(transaction, commission, received)

            if level == RiskLevel.MEDIUM:
                audit_level = AuditLevel.WARNING
            else:
                audit_level = AuditLevel.INFO

            if len(error_message) > 0:
                message = f"{transaction.get_amount()} -> OK ({'; '.join(error_message)})"

            self.__audit_log.record(audit_level, "transfer", transaction.get_sender().full_name,
                                     transaction.get_sender().get_account_number(), message)
        except InvalidOperationError as e:
            self.retry(transaction, str(e))
        except (AccountFrozenError, AccountClosedError, InsufficientFundsError) as e:
            self.fail(transaction, str(e))

    def validate(self, transaction: Transaction):
        limit = None
        required = transaction.get_amount() + self.commission(transaction)
        sender = transaction.get_sender()
        receiver = transaction.get_receiver()

        if receiver.get_status_account() == StatusAccount.FROZEN:
            raise AccountFrozenError("Замороженный счёт получателя")

        if receiver.get_status_account() == StatusAccount.CLOSE:
            raise AccountClosedError("Закрытый счёт получателя")

        if isinstance(sender, PremiumAccount) :
            limit = sender.balance() + sender.overdraft
        else:
            limit = sender.balance()

        if limit < required:
            raise InsufficientFundsError("недостаточно средств")


    def commission(self, transaction: Transaction) -> float:
        if (isinstance(transaction.get_sender(), PremiumAccount)
                or transaction.get_transaction_type() != TransactionType.TRANSFER_EXTERNAL):
            return 0.0

        return round(transaction.get_amount() * self.EXTERNAL_COMMISSION_RATE, 2)

    def convert_amount(self, transaction: Transaction) -> float:
        sender_currency = transaction.get_sender().get_currency_type()
        receiver_currency = transaction.get_receiver().get_currency_type()

        if sender_currency == receiver_currency:
            return transaction.get_amount()

        key = (sender_currency.value, receiver_currency.value)

        if key not in self.EXCHANGE_RATES:
            raise InvalidOperationError(f"Нет курса {sender_currency.value} -> {receiver_currency.value}")

        return round(transaction.get_amount() * self.EXCHANGE_RATES[key], 2)

    def execute(self, transaction: Transaction, commission: float, received_amount: float):
        transaction.set_commission(commission)
        transaction.get_sender().withdraw(transaction.get_amount() + commission)
        transaction.get_receiver().deposit(received_amount)
        transaction.set_status(TransactionStatus.COMPLETED)
        transaction.set_completed_at(datetime.now())
        self.__transaction_queue.remove_transaction(transaction)


    def retry(self, transaction: Transaction, reason: str):
        attempt = self.__attempts.get(transaction.get_id(), 1)
        self.__error_log.append((transaction.get_id(), reason, datetime.now(), f"retry {attempt}"))
        
        if attempt < self.MAX_ATTEMPTS:
            self.__attempts[transaction.get_id()] = attempt + 1
            transaction.set_status(TransactionStatus.RETRY)
        else:
            self.fail(transaction, f"исчерпаны попытки: {reason}")

    def fail(self, transaction: Transaction, reason: str):
        transaction.set_status(TransactionStatus.FAILED)
        self.__error_log.append((transaction.get_id(), reason, datetime.now(), "final"))
        self.__transaction_queue.remove_transaction(transaction)

        self.__audit_log.record(AuditLevel.ERROR, "transfer_failed", transaction.get_sender().full_name,
                                transaction.get_sender().get_account_number(), reason)

    def print_error_log(self):
        for tid, reason, time, kind in self.__error_log:
            print(f"{time:%H:%M:%S}  {tid}  [{kind}]  {reason}")