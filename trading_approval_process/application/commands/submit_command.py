from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.trade_action import TradeAction



class SubmitCommand:
    def __init__(self, repository: ITradeRepository, time: ITimeProvider):
        self._repository = repository
        self._time = time

    async def run(self, user: str, trade_id: str, token: CancellationToken) ->Trade:
        # Load
        trade = await self._repository.get_by_id(trade_id, token)

        # Validate
        trade.validate(user, TradeAction.SUBMIT)

        # Change
        trade.change(user, TradeAction.SUBMIT, self._time.now())

        # Save
        await self._repository.update(trade, token)

        return trade
