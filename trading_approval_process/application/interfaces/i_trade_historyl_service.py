from abc import ABC, abstractmethod

from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade_diff import TradeDiff
from trading_approval_process.domain.models.trade_history import TradeHistory


class ITradeHistoryService(ABC):


    @abstractmethod
    async def get_history(self, trade_id: str, token: CancellationToken) -> TradeHistory:
        """Return the complete audit trail of a trade."""
        raise NotImplementedError

    @abstractmethod
    async def get_differences(self, trade_id: str, version_a: int, version_b: int, token: CancellationToken) -> TradeDiff:
        """Show field-level differences between two versions of trade details."""
        raise NotImplementedError


