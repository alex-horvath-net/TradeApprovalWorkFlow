from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade_history import TradeHistory


class HistoryCommand:
    def __init__(self, repository: ITradeRepository):
        self._repository = repository

    async def run(self, trade_id: str, token: CancellationToken) ->TradeHistory:
        # Load
        trade = await self._repository.get_by_id(trade_id, token)

        # Return its full history
        return trade.to_history()
