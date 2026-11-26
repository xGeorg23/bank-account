from bank.audit.audit_log import AuditLog
from bank.audit.audit_report import AuditReport
from bank.audit.risk_analyzer import RiskAnalyzer
from bank.bank import Bank
from bank.client import Client
from bank.transaction.transaction import Transaction
from bank.transaction.transaction_processor import TransactionProcessor
from bank.transaction.transaction_queue import TransactionQueue
from util.account_type import AccountType
from util.currency import CurrencyType
from util.transaction_type import TransactionType


def separator(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    separator("1. Инициализация банка, клиентов и счетов")

    bank = Bank([])

    clients_data = [
        (1, "Иванов Иван Иванович", "+79551110001", 35, "pass1"),
        (2, "Петрова Анна Сергеевна", "+79551110002", 28, "pass2"),
        (3, "Сидоров Пётр Андреевич", "+79551110003", 45, "pass3"),
        (4, "Козлова Мария Олеговна", "+79551110004", 31, "pass4"),
        (5, "Смирнов Алексей Викторович", "+79551110005", 52, "pass5"),
        (6, "Новикова Елена Дмитриевна", "+79551110006", 24, "pass6"),
    ]
    clients = []
    for cid, name, phone, age, password in clients_data:
        c = Client(cid, name, [], [f"+{phone}"], age, password, 0)
        bank.add_client(c)
        clients.append(c)

    accounts_data = [
        (1, "1001", AccountType.DEBIT, CurrencyType.RUB),
        (1, "1002", AccountType.SAVINGS, CurrencyType.RUB),
        (2, "2001", AccountType.DEBIT, CurrencyType.RUB),
        (2, "2002", AccountType.SAVINGS, CurrencyType.USD),
        (3, "3001", AccountType.PREMIUM, CurrencyType.RUB),
        (3, "3002", AccountType.DEBIT, CurrencyType.EUR),
        (4, "4001", AccountType.DEBIT, CurrencyType.RUB),
        (4, "4002", AccountType.INVESTMENT, CurrencyType.RUB),
        (5, "5001", AccountType.PREMIUM, CurrencyType.RUB),
        (5, "5002", AccountType.DEBIT, CurrencyType.USD),
        (6, "6001", AccountType.DEBIT, CurrencyType.RUB),
        (6, "6002", AccountType.SAVINGS, CurrencyType.RUB),
    ]
    for client_id, number, acc_type, currency in accounts_data:
        bank.open_account(client_id, number, acc_type, currency)

    initial_amounts = {
        "1001": 150000, "1002": 300000, "2001": 80000, "2002": 5000,
        "3001": 500000, "3002": 2000, "4001": 40000, "4002": 120000,
        "5001": 900000, "5002": 800, "6001": 25000, "6002": 60000,
    }
    acc_by_number = {}
    for client_id, number, _, _ in accounts_data:
        bank.deposit(client_id, number, initial_amounts[number])
        acc_by_number[number] = bank.search_accounts(client_id, number)

    bank.freeze_account(4, "4001")

    print(f"Клиентов: {len(clients)}, счетов: {len(accounts_data)}")
    print("Счёт 4001 (Козлова) заморожен для демонстрации отказов")

    separator("2. Формирование очереди транзакций")

    audit_log = AuditLog("audit.log")
    analyzer = RiskAnalyzer(audit_log)
    queue = TransactionQueue()
    processor = TransactionProcessor(queue, audit_log, analyzer)
    report = AuditReport(audit_log)

    A = acc_by_number
    T = TransactionType.TRANSFER_INTERNAL
    E = TransactionType.TRANSFER_EXTERNAL
    RUB = CurrencyType.RUB

    transactions_data = [
        (T, 5000, "1001", "2001"), (T, 12000, "1002", "1001"),
        (T, 3000, "2001", "1001"), (T, 8000, "3001", "1002"),
        (T, 1500, "6001", "1001"), (T, 4500, "6002", "2001"),
        (T, 2500, "1001", "6001"), (T, 7000, "4002", "1002"),
        (T, 9500, "3001", "5002"), (T, 2000, "5002", "3001"),
        (E, 10000, "1001", "6001"), (E, 20000, "3001", "1001"),
        (T, 1000, "2002", "1001"),
        (T, 500, "3002", "2001"),
        (T, 250000, "3001", "1002"), (T, 180000, "5001", "4002"),
        (T, 1000, "1001", "2001"), (T, 1100, "1001", "2001"),
        (T, 1200, "1001", "2001"), (T, 1300, "1001", "2001"),
        (T, 200000, "1001", "6001"),
        (T, 5000, "1001", "4001"),
        (T, 999999999, "6001", "1001"),
        (T, 500000, "4001", "1001"),
        (T, 80000, "5002", "3001"),
        (T, 6000, "3001", "6002"), (T, 3500, "1002", "4002"),
        (T, 2200, "6001", "6002"), (T, 4800, "2001", "5002"),
        (T, 15000, "3001", "2001"), (T, 7500, "4002", "3001"),
        (T, 900, "6002", "1001"), (T, 11000, "1002", "2002"),
    ]

    added, rejected = 0, 0
    for i, (ttype, amount, sender_num, receiver_num) in enumerate(transactions_data, start=1):
        t = Transaction(i, ttype, RUB, amount, A[sender_num], A[receiver_num])
        try:
            queue.add(t)
            added += 1
        except Exception as e:
            rejected += 1
            print(f"  ✗ транзакция {i} отклонена при постановке: {e}")

    t_deferred = Transaction(100, T, RUB, 5000, A["1001"], A["2001"])
    queue.add(t_deferred)
    from datetime import datetime, timedelta
    queue.deferred_transactions(100, datetime.now() + timedelta(days=1))
    queue.cancel(100)

    print(f"\nПринято в очередь: {added} (+1 отложенная, отменена), отклонено при постановке: {rejected}")
    print(queue.__str__())

    separator("3. Обработка очереди процессором")

    processor.run()

    print("\nОчередь после обработки:")
    print(queue.__str__())

    print("\nЖурнал ошибок процессора:")
    processor.print_error_log()

    separator("4. Сценарий: счета и история клиента (Иванов)")

    client = bank.search_client(1)
    for account in client.list_bank_account():
        print(account.__str__())
        print()

    client_accounts = {a.get_account_number() for a in client.list_bank_account()}
    print("История транзакций клиента (из истории очереди):")
    for t in queue.get_history():
        sender_num = t.get_sender().get_account_number()
        receiver_num = t.get_receiver().get_account_number()
        if sender_num in client_accounts or receiver_num in client_accounts:
            print(f"  #{t.get_id()} {sender_num} -> {receiver_num} "
                  f"{t.get_amount()} {t.get_currency_type().value} — {t.get_status().value}"
                  + (f" ({t.get_failure_reason()})" if t.get_failure_reason() else ""))

    separator("4.1 Сценарий: подозрительные операции")
    print(report.suspicious_operations())

    separator("5. Отчёты")

    totals = []
    for c in clients:
        totals.append((c, bank.get_total_balance(c.id())))
    totals.sort(key=lambda pair: pair[1], reverse=True)
    print("Топ-3 клиентов по суммарному балансу:")
    for place, (c, total) in enumerate(totals[:3], start=1):
        print(f"{place}. {c.full_name()} — {total:,.0f}")

    print("\nСтатистика транзакций:")
    for status, count in queue.statistics().items():
        print(f"  {status.value}: {count}")

    print("\nСтатистика ошибок:")
    print(report.error_statistics())

    print("\nРиск-профили клиентов:")
    for c in clients:
        for account in c.list_bank_account():
            print(f"{report.client_risk_profile(c.full_name(), account.get_account_number())}")

    grand_total = sum(total for _, total in totals)
    print(f"\nОбщий баланс банка: {grand_total:,.0f}")

    print(f"\nЖурнал аудита сохранён в файл audit.log ({len(audit_log.get_audits())} записей)")


if __name__ == "__main__":
    main()
