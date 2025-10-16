from trading_approval_process.application.commands.differences_command import DifferencesCommand
from trading_approval_process.application.commands.history_command import HistoryCommand
from trading_approval_process.application.interfaces import ITradeRepository, ITimeProvider
from trading_approval_process.application.interfaces.i_trade_historyl_service import ITradeHistoryService
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain import TradeHistory, TradeDiff


class TradeHistoryService(ITradeHistoryService):
    """History service for trade details."""

    def __init__( self, repository: ITradeRepository, time: ITimeProvider) -> None:
        self._repository = repository
        self._time = time

    async def get_history(self, trade_id: str, token: CancellationToken) -> TradeHistory:
        return await HistoryCommand(self._repository).run(trade_id, token)

    async def get_differences(self, trade_id: str, version_a: int, version_b: int, token: CancellationToken) -> TradeDiff:
        return await DifferencesCommand(self._repository).run(trade_id, version_a, version_b, token)
