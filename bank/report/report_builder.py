import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bank.audit.audit_log import AuditLog
from bank.bank import Bank
from util.audit_level import AuditLevel


class ReportBuilder:

    def __init__(self, bank: Bank, audit_log: AuditLog):
        self.bank = bank
        self.audit_log = audit_log

    def client_report(self, client_id: int) -> str:
        client = self.bank.search_client(client_id)
        lines = [f"Отчёт по клиенту: {client.full_name()} (id={client.id()})", "-" * 50]

        for account in client.list_bank_account():
            lines.append(f"  {account.account_type.value:<11} {account.get_account_number():<8} "
                         f"{account.balance():>12,.2f} {account.get_currency_type().value}  "
                         f"[{account.get_status_account().value}]")

        lines.append("-" * 50)
        lines.append(f"  Итого: {self.bank.get_total_balance(client_id):>12,.2f}")
        entries = self.audit_log.filter(client_name=client.full_name())
        lines.append(f"  Операций в аудите: {len(entries)}")

        return "\n".join(lines)

    def bank_report(self) -> str:
        lines = ["Отчёт по банку", "-" * 50]
        total_clients = len(self.bank.clients)
        total_accounts = sum(len(c.list_bank_account()) for c in self.bank.clients)
        grand_total = sum(self.bank.get_total_balance(c.id()) for c in self.bank.clients)
        lines.append(f"  Клиентов: {total_clients}")
        lines.append(f"  Счетов: {total_accounts}")
        lines.append(f"  Общий баланс: {grand_total:,.2f}")
        lines.append(f"  Записей аудита: {len(self.audit_log.get_audits())}")

        return "\n".join(lines)

    def risk_report(self) -> str:
        lines = ["Отчёт по рискам", "-" * 50]
        suspicious = [e for e in self.audit_log.get_audits() if e.get_level() != AuditLevel.INFO]
        lines.append(f"  Подозрительных событий: {len(suspicious)}")

        for level in (AuditLevel.WARNING, AuditLevel.ERROR, AuditLevel.CRITICAL):
            count = len(self.audit_log.filter(level=level))
            lines.append(f"    {level.value}: {count}")

        for e in suspicious:
            lines.append(f"  {e}")

        return "\n".join(lines)

    def client_report_data(self, client_id: int) -> dict:
        client = self.bank.search_client(client_id)

        return {
            "client_id": client.id(),
            "full_name": client.full_name(),
            "accounts": [
                {
                    "number": a.get_account_number(),
                    "type": a.account_type.value,
                    "currency": a.get_currency_type().value,
                    "balance": a.balance(),
                    "status": a.get_status_account().value,
                }
                for a in client.list_bank_account()
            ],
            "total_balance": self.bank.get_total_balance(client_id),
        }

    def audit_rows(self) -> list[dict]:
        return [
            {
                "timestamp": e.get_timestamp().strftime("%Y-%m-%d %H:%M:%S"),
                "level": e.get_level().value,
                "action": e.get_action(),
                "client": e.get_client_name(),
                "account": e.get_account_number(),
                "details": e.get_details(),
            }
            for e in self.audit_log.get_audits()
        ]

    def export_to_json(self, data: dict, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_to_csv(self, rows: list[dict], path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def save_charts(self, out_dir: str, balance_history: list[tuple[str, float]] = None):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        type_counts = {}
        for client in self.bank.clients:
            for account in client.list_bank_account():
                key = account.account_type.value
                type_counts[key] = type_counts.get(key, 0) + 1

        fig, ax = plt.subplots()
        ax.pie(type_counts.values(), labels=type_counts.keys(), autopct="%1.0f%%")
        ax.set_title("Счета по типам")
        fig.savefig(out / "accounts_by_type.png", dpi=120)
        plt.close(fig)

        names = [c.full_name().split()[0] for c in self.bank.clients]
        balances = [self.bank.get_total_balance(c.id()) for c in self.bank.clients]
        fig, ax = plt.subplots()
        ax.bar(names, balances)
        ax.set_title("Балансы клиентов")
        ax.set_ylabel("Баланс")
        fig.savefig(out / "client_balances.png", dpi=120)
        plt.close(fig)

        if balance_history:
            labels = [str(i) for i, _ in balance_history]
            values = [v for _, v in balance_history]
            fig, ax = plt.subplots()
            ax.plot(labels, values, marker="o")
            ax.set_title("Движение баланса")
            ax.set_xlabel("Операция")
            ax.set_ylabel("Баланс")
            fig.savefig(out / "balance_history.png", dpi=120)
            plt.close(fig)

        return sorted(p.name for p in out.glob("*.png"))
