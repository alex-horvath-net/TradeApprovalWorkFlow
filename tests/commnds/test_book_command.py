from unittest.mock import AsyncMock

import pytest

from tests.fixture import Fixture
from trading_approval_process.application.commands.book_command import BookCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import InvalidTransitionException, AuthorizationException
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_state import TradeState


class TestBookCommand:

    async def test_both_requester_and_approver_can_book_trade_in_sent_to_counterparty_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_sent_to_counterparty()
        fixture.repo_mock.get_by_id.return_value = trade

        confirmation = fixture.build_execution_confirmation(trade)
        cmd = BookCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, confirmation, token)

        assert updated_trade.state_before == TradeState.SENT_TO_COUNTERPARTY
        assert updated_trade.state == TradeState.EXECUTED
        assert updated_trade.execution_confirmation is not None
        assert updated_trade.execution_confirmation.confirmation_id == "CONF12345"
        assert updated_trade.details.strike == 1.2345

    async def test_nobody_can_book_trade_out_of_sent_to_counterparty_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        confirmation = fixture.build_execution_confirmation(trade)
        cmd = BookCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
            await cmd.run(fixture.requester, trade.trade_id, confirmation, token)

    async def test_only_either_requester_or_approver_can_book_trade_in_sent_to_counterparty_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_sent_to_counterparty()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        confirmation = fixture.build_execution_confirmation(trade)
        cmd = BookCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        # Approver should not book – only requester allowed
        with pytest.raises(AuthorizationException):
           await  cmd.run("neiter_requester_nore_approver", trade.trade_id, confirmation, token)


    async def test_version_increment(self):
        fixture = Fixture()
        trade = fixture.build_valid_sent_to_counterparty()
        version = trade.version
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        confirmation = fixture.build_execution_confirmation(trade)
        cmd = BookCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, confirmation, token)

        assert updated_trade.version == version + 1

    async def test_audit_trail(self):
        fixture = Fixture()
        trade = fixture.build_valid_sent_to_counterparty()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        confirmation = fixture.build_execution_confirmation(trade)
        cmd = BookCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, confirmation, token)

        assert len(updated_trade.audit) >= 1
        record = updated_trade.audit[-1]
        assert record.action == TradeAction.BOOK
        assert record.user_id == fixture.requester
        assert record.state_before == TradeState.SENT_TO_COUNTERPARTY
        assert record.state_after == TradeState.EXECUTED
        assert record.timestamp == fixture.fixed_now
