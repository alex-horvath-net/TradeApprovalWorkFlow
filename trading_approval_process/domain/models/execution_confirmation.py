from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExecutionConfirmation:
    ticket_id: str
    confirmation_id: str
    counterparty: str
    strike: float
    timestamp: datetime

