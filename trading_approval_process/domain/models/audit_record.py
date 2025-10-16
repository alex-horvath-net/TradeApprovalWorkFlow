from dataclasses import dataclass
from datetime import datetime
from .trade_state import TradeState
from .trade_action import TradeAction
from .trade_details import TradeDetails

@dataclass(frozen=True)
class AuditRecord:
    step: int
    action: TradeAction
    user_id: str
    state_before: TradeState
    state_after: TradeState
    details: TradeDetails
    timestamp: datetime
    notes: str | None = None

    def __str__(self) -> str:
        """Return a concise human-readable summary for testing and logging."""
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"Step: {self.step} | "
            f"Action: {self.action.name} | "
            f"User ID: {self.user_id} | "
            f"State Before: {self.state_before.name} | "
            f"State After: {self.state_after.name} | "
            f"Notes: {self.notes}"
        )