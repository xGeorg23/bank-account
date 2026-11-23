from bank.bank import Bank
from bank.client import Client
from bank.transaction.transaction import Transaction
from bank.transaction.transaction_processor import TransactionProcessor
from bank.transaction.transaction_queue import TransactionQueue
from bank.audit.audit_log import AuditLog
from bank.audit.risk_analyzer import RiskAnalyzer
from bank.report.report_builder import ReportBuilder
from util.account_type import AccountType
from util.currency import CurrencyType
from util.transaction_type import TransactionType


def main():
    bank = Bank([])
    ivan = Client(1, "Иванов Иван Иванович", [], ["+7955001"], 35, "pass1", 0)
    anna = Client(2, "Петрова Анна Сергеевна", [], ["+7955002"], 28, "pass2", 0)
    bank.add_client(ivan)
    bank.add_client(anna)

    bank.open_account(1, "1001", AccountType.DEBIT, CurrencyType.RUB)
    bank.open_account(1, "1002", AccountType.SAVINGS, CurrencyType.RUB)
    bank.open_account(2, "2001", AccountType.DEBIT, CurrencyType.RUB)
    bank.open_account(2, "2002", AccountType.PREMIUM, CurrencyType.RUB)

    acc = {n: bank.search_accounts(cid, n)
           for cid, n in ((1, "1001"), (1, "1002"), (2, "2001"), (2, "2002"))}

    balance_history = []

    def track(account, label):
        balance_history.append((label, account.balance()))

    bank.deposit(1, "1001", 100000);  track(acc["1001"], "старт")
    bank.deposit(1, "1002", 200000)
    bank.deposit(2, "2001", 50000)
    bank.deposit(2, "2002", 300000)

    audit_log = AuditLog()
    analyzer = RiskAnalyzer(audit_log)
    queue = TransactionQueue()
    processor = TransactionProcessor(queue, audit_log, analyzer)

    T = TransactionType.TRANSFER_INTERNAL
    E = TransactionType.TRANSFER_EXTERNAL
    queue.add(Transaction(1, T, CurrencyType.RUB, 10000, acc["1001"], acc["2001"]))
    queue.add(Transaction(2, T, CurrencyType.RUB, 25000, acc["1002"], acc["1001"]))
    queue.add(Transaction(3, E, CurrencyType.RUB, 5000, acc["2001"], acc["1001"]))
    queue.add(Transaction(4, T, CurrencyType.RUB, 99999999, acc["2001"], acc["1001"]))

    processor.run()
    track(acc["1001"], "после переводов")

    bank.withdraw(1, "1001", 15000);  track(acc["1001"], "снятие")
    bank.deposit(1, "1001", 40000);   track(acc["1001"], "пополнение")
    bank.withdraw(1, "1001", 8000);   track(acc["1001"], "снятие 2")

    builder = ReportBuilder(bank, audit_log)

    print(builder.client_report(1))
    print()
    print(builder.bank_report())
    print()
    print(builder.risk_report())
    print()

    builder.export_to_json(builder.client_report_data(1), "reports/report_client_1.json")
    builder.export_to_json({"bank": builder.bank_report()}, "reports/report_bank.json")
    builder.export_to_csv(builder.audit_rows(), "reports/audit_log.csv")
    print("Экспорт: reports/report_client_1.json, report_bank.json, audit_log.csv")

    charts = builder.save_charts("reports", balance_history=balance_history)
    print("Графики:", ", ".join(f"reports/{name}" for name in charts))


test_()
