from abc import ABC, abstractmethod

from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.execution_confirmation import ExecutionConfirmation
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.trade_details import TradeDetails


class ITradeApprovalService(ABC):
    """Trade approval service for workflow."""

    @abstractmethod
    async def create(self, user: str, details: TradeDetails, token: CancellationToken) -> Trade:
        """Create a new trade in DRAFT state."""
        raise NotImplementedError

    @abstractmethod
    async def submit(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        """Submit a trade for approval (Draft → PendingApproval)."""
        raise NotImplementedError

    @abstractmethod
    async def approve(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        """Approve a trade in PendingApproval or NeedsReapproval state."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: str, trade_id: str, details: TradeDetails, token: CancellationToken) -> Trade:
        """Update trade details (Draft or PendingApproval)."""
        raise NotImplementedError

    @abstractmethod
    async def cancel(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        """Cancel a trade (Requester or Approver)."""
        raise NotImplementedError

    @abstractmethod
    async def send_to_execute(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        """Send an approved trade to the counterparty for execution."""
        raise NotImplementedError

    @abstractmethod
    async def book(self, user: str, trade_id: str, confirmation: ExecutionConfirmation, token: CancellationToken) -> Trade:
        """Book a trade once executed by counterparty."""
        raise NotImplementedError
