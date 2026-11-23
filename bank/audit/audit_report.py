from collections import Counter

from bank.audit.audit_log import AuditLog
from util.audit_level import AuditLevel


class AuditReport:
    __audit_log: AuditLog

    def __init__(self, audit_log: AuditLog):
        self.__audit_log = audit_log

    def suspicious_operations(self) -> str:
        entries = []
        lines = ["Подозрительные операции:"]

        for e in self.__audit_log.get_audits():
            if e.get_level() != AuditLevel.INFO:
                entries.append(e)

        if not entries:
            return "Подозрительных операций нет"

        for e in entries:
            lines.append(f" {e}")

        return "\n".join(lines)

    def client_risk_profile(self, client_name: str, account_number:str) -> str:
        entries = self.__audit_log.filter(client_name=client_name, account_number=account_number)

        if not entries:
            return f"{client_name}, {account_number}: операций нет"

        total = len(entries)
        warnings = sum(1 for e in entries if e.get_level() == AuditLevel.WARNING)
        critical = sum(1 for e in entries if e.get_level() == AuditLevel.CRITICAL)
        errors = sum(1 for e in entries if e.get_level() == AuditLevel.ERROR)

        if critical > 0 or warnings >= 3:
            profile = "высокий"
        elif warnings > 0 or errors >= 2:
            profile = "средний"
        else:
            profile = "низкий"

        return (f"{client_name}: операций {total}, подозрительных {warnings}, "
                f"заблокировано {critical}, ошибок {errors} — профиль риска: {profile}")

    def error_statistics(self) -> str:
        errors = self.__audit_log.filter(level=AuditLevel.ERROR)

        if not errors:
            return "Ошибок нет"

        counts = Counter(e.get_details() for e in errors)
        lines = ["Статистика ошибок:"]

        for reason, count in counts.most_common():
            lines.append(f" {reason}: {count}")

        return "\n".join(lines)
