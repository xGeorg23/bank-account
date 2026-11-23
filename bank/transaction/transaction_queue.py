from datetime import datetime

from exception.bank_exception import AccountFrozenError, TransactionError
from bank.transaction.transaction import Transaction
from util.account_type import AccountType
from util.status_account import StatusAccount
from util.transaction_status import TransactionStatus

class TransactionQueue: 
    transactions: list[Transaction]

    def __init__(self): 
        self.transactions = []

    def add(self, transaction: Transaction):
        self.validation_transaction(transaction)
        transaction.set_status(TransactionStatus.PENDING)
        self.transactions.append(transaction)
        self.priority()

    def get_transactions(self) -> list[Transaction]:
        return self.transactions

    def priority(self):
        for t in self.transactions:
            if t.get_sender().get_account_type() == AccountType.PREMIUM:
                t.set_priority(1)
            else :
                t.set_priority(2)

        self.transactions.sort(key=lambda t: t.get_priority())

    def deferred_transactions(self, transaction_id:int, deferred_at:datetime):
        for t in self.transactions:
            if t.get_id() == transaction_id:
                t.set_deferred_at(deferred_at)

    def cancel(self, transaction_id: int):
        for transaction in self.transactions:
            if transaction.get_id() == transaction_id:
                if transaction.get_status() != TransactionStatus.COMPLETED:
                    transaction.set_status(TransactionStatus.CANCELLED)
                    self.remove_transaction(transaction)
                else:
                    raise TransactionError("Транзакция выполнена")

    def remove_transaction(self, transaction: Transaction):
        if (transaction.get_status() == TransactionStatus.COMPLETED
                or transaction.get_status() == TransactionStatus.CANCELLED
                or transaction.get_status() == TransactionStatus.FAILED):
            self.transactions.remove(transaction)

    def __str__(self): 
        lines = [f"В очереди: {len(self.transactions)} транзакций"]

        for t in self.transactions: 
            lines.append(f"  {t}")

        return "\n".join(lines)

    @staticmethod
    def validation_transaction(transaction: Transaction):
        sender = transaction.get_sender()
        receiver = transaction.get_receiver()

        if (receiver.get_status_account() == StatusAccount.FROZEN
                or receiver.get_status_account() == StatusAccount.CLOSE):
            raise AccountFrozenError("Аккаунт получателя заморожен или закрыт")