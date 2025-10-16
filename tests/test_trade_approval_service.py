from datetime import timedelta
from dataclasses import replace
import pytest

from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.application.services.trade_approval_service import TradeApprovalService
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import AuthorizationException, InvalidTransitionException
from trading_approval_process.domain.models.execution_confirmation import ExecutionConfirmation
from trading_approval_process.domain.models.trade_details import TradeDetails
from trading_approval_process.domain.models.trade_direction import TradeDirection
from trading_approval_process.domain.models.trade_style import TradeStyle
from trading_approval_process.infrastructure import SystemTime, InMemoryTradeRepository, InmemoryTradeExecutor


class TestApprovalService:

    async def test_end_to_end(self):
        time : ITimeProvider = SystemTime()
        repository: ITradeRepository = InMemoryTradeRepository()
        executor: InmemoryTradeExecutor = InmemoryTradeExecutor()
        service = TradeApprovalService(executor, repository, time)
        token = CancellationToken()
        details = TradeDetails(
            trading_entity="BankA",
            counterparty="BankB",
            direction=TradeDirection.BUY,
            style=TradeStyle.FORWARD,
            notional_currency="USD",
            notional_amount=1_000_000,
            underlying="USD/EUR",
            trade_date=time.now(),
            value_date=time.now() + timedelta(days=2),
            delivery_date=time.now() + timedelta(days=5),
        )

        # CREATE
        trade = await service.create("user1", details, token)
        assert str(trade.audit[-1]) == "Step: 1 | Action: CREATE | User ID: user1 | State Before: INITIAL | State After: DRAFT | Notes: Trade created"

        # UPDATE
        details_to_update = replace(trade.details, notional_amount=2_000_000)
        with pytest.raises(AuthorizationException):
            await service.update("user2", trade.trade_id, details_to_update, token)
        trade = await service.update("user1", trade.trade_id, details_to_update, token)
        assert str(trade.audit[-1]) == "Step: 2 | Action: UPDATE | User ID: user1 | State Before: DRAFT | State After: DRAFT | Notes: Trade updated"

        # SUBMIT
        with pytest.raises(AuthorizationException):
            await service.submit("user2", trade.trade_id, token)
        trade = await service.submit("user1", trade.trade_id, token)
        assert str(trade.audit[-1]) == "Step: 3 | Action: SUBMIT | User ID: user1 | State Before: DRAFT | State After: PENDING_APPROVAL | Notes: Trade submitted"

        # UPDATE
        new_details_to_update = replace(trade.details, notional_amount=3_000_000)
        with pytest.raises(AuthorizationException):
            await service.update("user1", trade.trade_id, new_details_to_update, token)
        trade = await service.update("user2", trade.trade_id, new_details_to_update, token)
        assert str(trade.audit[-1]) == "Step: 4 | Action: UPDATE | User ID: user2 | State Before: PENDING_APPROVAL | State After: NEEDS_REAPPROVAL | Notes: Trade updated, need reapproval"

        # APPROVE
        with pytest.raises(AuthorizationException):
            await service.approve("user2", trade.trade_id, token)
        trade = await service.approve("user1", trade.trade_id, token)
        assert str(trade.audit[-1]) == "Step: 5 | Action: APPROVE | User ID: user1 | State Before: NEEDS_REAPPROVAL | State After: APPROVED | Notes: Trade reapproved"

        # SEND_TO_EXECUTE
        with pytest.raises(AuthorizationException):
            await service.send_to_execute("user2", trade.trade_id, token)
        trade = await service.send_to_execute("user1", trade.trade_id, token)
        assert str(trade.audit[-1]) == "Step: 6 | Action: SEND_TO_EXECUTE | User ID: user1 | State Before: APPROVED | State After: SENT_TO_COUNTERPARTY | Notes: Trade sent to counterparty"

        # BOOK
        confirmation = ExecutionConfirmation(
            ticket_id= trade.execution_receipt.ticket_id,
            confirmation_id= "CONF12345",
            counterparty= trade.details.counterparty,
            strike= 1.2345,
            timestamp=time.now(),
        )
        trade = await service.book("user1", trade.trade_id, confirmation, token)
        assert str(trade.audit[-1]) == "Step: 7 | Action: BOOK | User ID: user1 | State Before: SENT_TO_COUNTERPARTY | State After: EXECUTED | Notes: Trade executed"

        # CANCEL
        with pytest.raises(InvalidTransitionException):
            await service.cancel("user2", trade.trade_id, token)