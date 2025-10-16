from enum import Enum, auto

class TradeState(Enum):
    INITIAL = auto()
    DRAFT = auto()
    PENDING_APPROVAL = auto()
    NEEDS_REAPPROVAL = auto()
    APPROVED = auto()
    SENT_TO_COUNTERPARTY = auto()
    EXECUTED = auto()
    CANCELLED = auto()
