from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExecutionReceipt:
    ticket_id: str
    sent_at: datetime
    venue: str
    status: str
    notes: str
