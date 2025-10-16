from trading_approval_process.application.commands.approve_command import ApproveCommand
from trading_approval_process.application.commands.book_command import BookCommand
from trading_approval_process.application.commands.cancel_command import CancelCommand
from trading_approval_process.application.commands.create_command import CreateCommand
from trading_approval_process.application.commands.send_to_execute_command import SendToExecuteCommand
from trading_approval_process.application.commands.submit_command import SubmitCommand
from trading_approval_process.application.commands.update_command import UpdateCommand
from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_approval_service import ITradeApprovalService
from trading_approval_process.application.interfaces.i_trade_executor import ITradeExecutor
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.domain.models.execution_confirmation import ExecutionConfirmation
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.trade_details import TradeDetails


class TradeApprovalService(ITradeApprovalService):
    """Trade approval service for workflow."""

    def __init__( self, executor: ITradeExecutor, repository: ITradeRepository, time: ITimeProvider) -> None:
        self._executor = executor
        self._repository = repository
        self._time = time

    async def create(self, user: str, details: TradeDetails, token: CancellationToken) -> Trade:
        return await CreateCommand(self._repository, self._time).run(user, details, token)

    async def submit(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        return await SubmitCommand(self._repository, self._time).run(user, trade_id, token)

    async def approve(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        return await ApproveCommand(self._repository, self._time).run(user, trade_id, token)

    async def update(self, user: str, trade_id: str, details: TradeDetails, token: CancellationToken) -> Trade:
        return await UpdateCommand(self._repository, self._time).run(user, trade_id, details, token)

    async def cancel(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        return await CancelCommand(self._repository, self._time).run(user, trade_id, token)

    async def send_to_execute(self, user: str, trade_id: str, token: CancellationToken) -> Trade:
        return await SendToExecuteCommand(self._executor, self._repository, self._time).run(user, trade_id, token)

    async def book(self, user: str, trade_id: str, confirmation: ExecutionConfirmation,
                   token: CancellationToken) -> Trade:
        return await BookCommand(self._repository, self._time).run(user, trade_id, confirmation, token)



