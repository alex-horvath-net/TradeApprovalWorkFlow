from abc import ABC, abstractmethod

from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.execution_receipt import ExecutionReceipt

class ITradeExecutor(ABC):
    """Abstract interface for sending trades to counterparties or execution systems."""

    @abstractmethod
    async def send(self, trade: Trade, token: CancellationToken) -> ExecutionReceipt:
        """Send a trade for external execution."""
        pass
