from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_executor import ITradeExecutor
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.trade_action import TradeAction


class SendToExecuteCommand:

    def __init__(self, executor: ITradeExecutor, repository: ITradeRepository, time: ITimeProvider):
        self._executor = executor
        self._repository = repository
        self._time = time


    async def run(self, user: str, trade_id: str, token: CancellationToken) ->Trade:
        # Load
        trade = await  self._repository.get_by_id(trade_id, token)

        # Validate
        trade.validate(user, TradeAction.SEND_TO_EXECUTE)

        # Change
        trade.execution_receipt = await self._executor.send(trade, token)
        trade.change(user, TradeAction.SEND_TO_EXECUTE, self._time.now())

        # Save
        await self._repository.update(trade, token)

        return trade
