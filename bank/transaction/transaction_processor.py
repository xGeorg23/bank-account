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
    InvalidOperationError, )
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
                 audit_log: AuditLog = None, risk_analyzer: RiskAnalyzer = None):
        self.__transaction_queue = transaction_queue
        self.__audit_log = audit_log or AuditLog()
        self.__risk_analyzer = risk_analyzer or RiskAnalyzer(self.__audit_log)
        self.__attempts = {}
        self.__error_log = []

    def run(self):
        for transaction in list(self.__transaction_queue.get_transactions()):
            deferred = transaction.get_deferred_at()
            if deferred is not None and datetime.now() < deferred:
                continue
            self.process(transaction)

            while transaction.get_status() == TransactionStatus.RETRY:
                self.process(transaction)

    def process(self, transaction: Transaction):
        audit_level: AuditLevel
        try:
            self.validate(transaction)
            commission = self.commission(transaction)
            debit = self.convert_amount(transaction, transaction.get_sender().get_currency_type(),
                                        transaction.get_amount() + commission)
            received = self.convert_amount(transaction, transaction.get_receiver().get_currency_type(),
                                           transaction.get_amount())
            level, error_message = next(iter(self.__risk_analyzer.analyze(transaction).items()))

            if level == RiskLevel.HIGH:
                self.__audit_log.record(AuditLevel.CRITICAL, "transfer_blocked", transaction.get_sender().full_name,
                                        transaction.get_sender().get_account_number(), "; ".join(error_message))
                self.fail(transaction, f"Операция заблокирована: {'; '.join(error_message)}")
                return
            self.execute(transaction, commission, debit, received)

            if level == RiskLevel.MEDIUM:
                audit_level = AuditLevel.WARNING
            else:
                audit_level = AuditLevel.INFO

            message = (f"{transaction.get_amount()} {transaction.get_currency_type().value} "
                       f"-> {transaction.get_receiver().get_account_number()} OK")
            if len(error_message) > 0:
                message += f" ({'; '.join(error_message)})"

            self.__audit_log.record(audit_level, "transfer", transaction.get_sender().full_name,
                                     transaction.get_sender().get_account_number(), message)
        except InvalidOperationError as e:
            self.retry(transaction, str(e))
        except (AccountFrozenError, AccountClosedError, InsufficientFundsError) as e:
            self.fail(transaction, str(e))

    def validate(self, transaction: Transaction):
        limit = None
        sender = transaction.get_sender()
        receiver = transaction.get_receiver()
        required = self.convert_amount(transaction, sender.get_currency_type(),
                                       transaction.get_amount() + self.commission(transaction))

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

    def convert_amount(self, transaction: Transaction, target_currency, amount: float) -> float:
        source_currency = transaction.get_currency_type()

        if source_currency == target_currency:
            return amount

        rate = self.exchange_rate(source_currency, target_currency)
        return round(amount * rate, 2)

    def exchange_rate(self, source_currency, target_currency) -> float:
        key = (source_currency.value, target_currency.value)
        reverse_key = (target_currency.value, source_currency.value)

        if key in self.EXCHANGE_RATES:
            return self.EXCHANGE_RATES[key]
        if reverse_key in self.EXCHANGE_RATES:
            return 1 / self.EXCHANGE_RATES[reverse_key]

        raise InvalidOperationError(f"Нет курса {source_currency.value} -> {target_currency.value}")

    def execute(self, transaction: Transaction, commission: float, debit_amount: float, received_amount: float):
        transaction.set_commission(commission)
        transaction.get_sender().withdraw(debit_amount)
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
        transaction.set_failure_reason(reason)
        transaction.set_completed_at(datetime.now())
        self.__error_log.append((transaction.get_id(), reason, datetime.now(), "final"))
        self.__transaction_queue.remove_transaction(transaction)

        self.__audit_log.record(AuditLevel.ERROR, "transfer_failed", transaction.get_sender().full_name,
                                transaction.get_sender().get_account_number(), reason)

    def print_error_log(self):
        for tid, reason, time, kind in self.__error_log:
            print(f"{time:%H:%M:%S}  {tid}  [{kind}]  {reason}")