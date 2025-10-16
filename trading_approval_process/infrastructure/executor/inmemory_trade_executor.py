from datetime import datetime, UTC
import asyncio

from trading_approval_process.application.interfaces.i_trade_executor import ITradeExecutor
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.execution_receipt import ExecutionReceipt
from trading_approval_process.domain.models.trade import Trade


class InmemoryTradeExecutor(ITradeExecutor):
    async def send(self, trade: Trade, token: CancellationToken) -> ExecutionReceipt:
        """Simulates sending trade to counterparty, returns a fake receipt"""
        await asyncio.sleep(0.01)
        await token.throw_if_cancellation_requested()

        return ExecutionReceipt(
            ticket_id=f"TICKET-{trade.trade_id}",
            sent_at=datetime.now(UTC),
            venue="NOOP",
            status="SENT",
            notes="Simulated execution"
        )
