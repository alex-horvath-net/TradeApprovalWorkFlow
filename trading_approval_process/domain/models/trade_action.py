from enum import Enum, auto

class TradeAction(Enum):
    CREATE = auto()
    UPDATE = auto()
    SUBMIT = auto()
    CANCEL = auto()
    APPROVE = auto()
    SEND_TO_EXECUTE = auto()
    BOOK = auto()
