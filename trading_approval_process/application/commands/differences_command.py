from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade_diff import TradeDiff


class DifferencesCommand:
    def __init__(self, repository: ITradeRepository):
        self._repository = repository

    async def run(self, trade_id: str, version_a: int, version_b: int, token: CancellationToken) ->TradeDiff:
        # Load
        trade = await self._repository.get_by_id(trade_id, token)

        return trade.get_differences(version_a, version_b)
