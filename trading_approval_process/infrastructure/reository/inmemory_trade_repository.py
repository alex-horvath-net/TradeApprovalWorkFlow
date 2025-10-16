import asyncio
import copy
from typing import Dict

from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions.concurent_exception import ConcurrencyException
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.exceptions import NotFoundException


class InMemoryTradeRepository(ITradeRepository):
    """Thread-unsafe in-memory repository for testing and prototyping."""

    def __init__(self) -> None:
        self._store: Dict[str, Trade] = {}

    async def add(self, trade: Trade, token: CancellationToken) -> Trade:
        if trade.trade_id in self._store:
            raise ValueError(f"Trade with id {trade.trade_id} already exists")
        # store a safe cloned snapshot
        self._store[trade.trade_id] = self._clone_trade(trade)
        await asyncio.sleep(0)
        await token.throw_if_cancellation_requested()

        return trade

    async def get_by_id(self, trade_id: str, token: CancellationToken) -> Trade:
        if trade_id not in self._store:
            raise NotFoundException(f"Trade {trade_id} not found")
        # return a fresh cloned instance
        trade = self._clone_trade(self._store[trade_id])
        await asyncio.sleep(0)
        await token.throw_if_cancellation_requested()
        return trade

    async def update(self, trade: Trade, token: CancellationToken) -> None:
        if trade.trade_id not in self._store:
            raise NotFoundException(f"Trade {trade.trade_id} not found")

        existing = self._store[trade.trade_id]
        if existing.version != trade.version - 1:
            raise ConcurrencyException(
                f"Trade {trade.trade_id} version mismatch. "
                f"Expected {trade.version - 1}, found {existing.version}"
            )

        # replace snapshot with a cloned version
        self._store[trade.trade_id] = self._clone_trade(trade)
        await asyncio.sleep(0)
        token.throw_if_cancellation_requested()

    def _clone_trade(self, trade: Trade) -> Trade:
        """Create a safe shallow copy of Trade, excluding immutable MappingProxyType fields."""
        clone = copy.copy(trade)
        # Deepcopy only mutable fields
        clone.details = copy.deepcopy(trade.details)
        clone.audit = copy.deepcopy(trade.audit)
        clone.execution_receipt = copy.deepcopy(trade.execution_receipt)
        clone.execution_confirmation = copy.deepcopy(trade.execution_confirmation)
        return clone
