from unittest.mock import AsyncMock

import pytest

from tests.fixture import Fixture
from trading_approval_process.application.commands.approve_command import ApproveCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.models.trade_state import TradeState
from trading_approval_process.domain.models.trade_action import  TradeAction
from trading_approval_process.domain.exceptions import InvalidTransitionException, AuthorizationException

class TestApproveCommand:

    async def test_everyone_except_requester_can_approve_trade_in_pending_approval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        cmd = ApproveCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.PENDING_APPROVAL
        assert updated_trade.state == TradeState.APPROVED
        assert updated_trade.approver == fixture.none_requester

    async def test_only_requester_can_approve_trade_in_needs_reapproval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_needs_reapproval()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        cmd = ApproveCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.NEEDS_REAPPROVAL
        assert updated_trade.state == TradeState.APPROVED
        assert updated_trade.approver == fixture.requester

    async def test_nobody_can_approve_trade_out_of_pending_approval_or_needs_reapproval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        cmd = ApproveCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
            await cmd.run(fixture.requester, trade.trade_id, token)

    async def test_requester_can_not_approve_trade_in_pending_approval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        cmd = ApproveCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        # requester is not allowed to approve
        with pytest.raises(AuthorizationException):
            await cmd.run(fixture.requester, trade.trade_id, token)


    async def test_version_increment(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        version = trade.version
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = ApproveCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert updated_trade.version == version + 1

    async def test_audit_trail(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        fixture.repo_mock.get_by_id = AsyncMock(return_value=trade)
        cmd = ApproveCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert len(updated_trade.audit) >= 1
        record = updated_trade.audit[-1]
        assert record.action == TradeAction.APPROVE
        assert record.user_id == fixture.none_requester
        assert record.state_before == TradeState.PENDING_APPROVAL
        assert record.state_after == TradeState.APPROVED
        assert record.timestamp == fixture.fixed_now
