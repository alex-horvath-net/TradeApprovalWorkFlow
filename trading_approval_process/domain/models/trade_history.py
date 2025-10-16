from dataclasses import dataclass
import uuid
from trading_approval_process.domain.models.audit_record import AuditRecord


@dataclass(frozen=True)
class TradeHistory:
    trade_id: uuid.UUID
    requester: str
    approver: str | None
    records: list[AuditRecord]
