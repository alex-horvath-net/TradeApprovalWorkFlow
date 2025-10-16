
from dataclasses import replace

from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.execution_confirmation import ExecutionConfirmation
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.trade_action import TradeAction


class BookCommand:
    def __init__(self, repository: ITradeRepository, time: ITimeProvider):
        self._repository = repository
        self._time = time

    async def run(self, user: str, trade_id: str, confirmation: ExecutionConfirmation, token: CancellationToken) ->Trade:
        # Load
        trade = await self._repository.get_by_id(trade_id, token)

        # Validate
        trade.validate(user, TradeAction.BOOK)

        # Change
        trade.execution_confirmation = confirmation
        trade.details = replace( trade.details,
            strike=confirmation.strike,
            confirmation_id=confirmation.confirmation_id
        )
        trade.change(user, TradeAction.BOOK, self._time.now())

        # Save
        await self._repository.update(trade, token)

        return trade