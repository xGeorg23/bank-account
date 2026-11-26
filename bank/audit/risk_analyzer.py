from datetime import datetime, time

from bank.audit.audit_log import AuditLog
from util.risk_level import RiskLevel


class RiskAnalyzer:

    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log

    def analyze(self, transaction, now: datetime = None):
        reasons = []
        score = 0
        recent = []
        receiver = transaction.get_receiver()
        created_at = getattr(receiver, "created_at", None)

        if now is None:
            now = datetime.now()

        if transaction.get_amount() > 100000:
            score += 2
            reasons.append(f"крупная сумма: {transaction.get_amount()}")

        for e in self.audit_log.filter(client_name=transaction.get_sender().full_name):
            if 0 <= (now - e.get_timestamp()).total_seconds() < 3600:
                recent.append(e)

        if len(recent) >= 3:
            score += 2
            reasons.append(f"частые операции: {len(recent)} за час")

        if created_at is not None and (now - created_at).days < 30:
            score += 1
            reasons.append("перевод на новый счёт")

        if time(0, 0) <= now.time() < time(5, 0):
            score += 1
            reasons.append("ночная операция")

        if score >= 4:
            return {RiskLevel.HIGH: reasons}
        if score >= 2:
            return {RiskLevel.MEDIUM: reasons}

        return {RiskLevel.LOW: reasons}
