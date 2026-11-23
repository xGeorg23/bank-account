from util.audit_level import AuditLevel
from bank.audit.audit_entry import Audit


class AuditLog:

    __audits: list[Audit]
    __log_file: str | None

    def __init__(self, log_file: str = None):
        self.__audits = []
        self.__log_file = log_file

    def record(self, level: AuditLevel, action: str, client_name: str, account_number: str, details: str):
        audit = Audit(level, action, client_name, account_number, details)
        self.__audits.append(audit)

        if self.__log_file is not None:
            with open(self.__log_file, "a", encoding="utf-8") as f:
                f.write(str(audit) + "\n")

    def filter(self, level: AuditLevel = None, client_name: str = None, account_number: str= None, action: str = None) -> list[Audit]:
        result = []

        for a in self.__audits:
            if ((level is None or a.get_level() == level)
                and (client_name is None or a.get_client_name() == client_name)
                and (account_number is None or a.get_account_number() == account_number)
                and (action is None or a.get_action() == action)):
                result.append(a)

        return result

    def get_audits(self) -> list[Audit]:
        return self.__audits

    def get_log_file(self) -> str | None:
        return self.__log_file

    def __str__(self):
        lines = [f"Записей в журнале: {len(self.__audits)}"]
        for a in self.__audits:
            lines.append(f"  {a}")
        return "\n".join(lines)
