from abc import ABC, abstractmethod
from uuid import UUID

from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade import Trade


class ITradeRepository(ABC):
    """Abstract interface for trade persistence."""

    @abstractmethod
    async def add(self, trade: Trade, token: CancellationToken) -> Trade:
        """Persist a new trade instance."""
        pass

    @abstractmethod
    async def update(self, trade: Trade, token: CancellationToken) -> Trade:
        """Persist updated trade state."""
        pass

    @abstractmethod
    async def get_by_id(self, trade_id: str, token: CancellationToken) -> Trade:
        """Retrieve a trade by its unique identifier."""
        pass


