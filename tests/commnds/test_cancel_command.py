import pytest
from tests.fixture import Fixture
from trading_approval_process.application.commands.cancel_command import CancelCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import InvalidTransitionException, AuthorizationException
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_state import TradeState


class TestCancelCommand:
    async def test_only_requester_can_cancel_trade_in_draft_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.DRAFT
        assert updated_trade.state == TradeState.CANCELLED

    async def test_everybody_except_requester_can_cancel_trade_in_pending_approval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.PENDING_APPROVAL
        assert updated_trade.state == TradeState.CANCELLED

    async def test_only_requester_can_cancel_trade_in_needs_reapproval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_needs_reapproval()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.NEEDS_REAPPROVAL
        assert updated_trade.state == TradeState.CANCELLED

    async def test_only_approver_can_cancel_trade_in_approved_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_approved_from_pending_approval()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(trade.approver, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.APPROVED
        assert updated_trade.state == TradeState.CANCELLED

    async def test_both_requester_and_approver_but_no_one_else_can_cancel_trade_in_sent_to_counterparty_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_sent_to_counterparty()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        # both requester and approver can cancel it
        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.SENT_TO_COUNTERPARTY
        assert updated_trade.state == TradeState.CANCELLED


    async def test_no_one_can_cancel_trade_in_executed_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_executed()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
            await cmd.run(fixture.requester, trade.trade_id, token)

    async def test_no_one_can_recancel_trade_in_canceled_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_cancelled()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
           await  cmd.run(fixture.requester, trade.trade_id, token)


    async def test_version_increment(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        version = trade.version
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert updated_trade.version == version + 1

    async def test_audit_trail(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = CancelCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        record = updated_trade.audit[-1]
        assert record.action == TradeAction.CANCEL
        assert record.user_id == fixture.requester
        assert record.state_before == TradeState.DRAFT
        assert record.state_after == TradeState.CANCELLED
        assert record.timestamp == fixture.fixed_now
        assert record.details == trade.details
