from ..application.interfaces.i_trade_executor import ITradeExecutor
from ..application.interfaces.i_time_provider import  ITimeProvider
from ..application.interfaces.i_trade_repository import ITradeRepository
from ..application.services.trade_approval_service import TradeApprovalService
from ..infrastructure import InmemoryTradeExecutor, SystemTime, InMemoryTradeRepository


def get_trade_service() -> TradeApprovalService:
    repo: ITradeRepository = InMemoryTradeRepository()
    executor: ITradeExecutor = InmemoryTradeExecutor()
    time:ITimeProvider = SystemTime()
    return TradeApprovalService(repo, time, executor)
