
from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_details import TradeDetails


class CreateCommand:
    def __init__(self, repository: ITradeRepository, time: ITimeProvider):
        self._repository = repository
        self._time = time

    async def run(self, user: str, trade_details: TradeDetails, token: CancellationToken) ->Trade:
        # Create
        trade: Trade = Trade()

        # Validate
        trade.validate(user, TradeAction.CREATE,  trade_details)

        # Change
        trade.requester = user
        trade.details = trade_details
        trade.change(user, TradeAction.CREATE, self._time.now())

        # Save
        await self._repository.add(trade, token)

        return trade
