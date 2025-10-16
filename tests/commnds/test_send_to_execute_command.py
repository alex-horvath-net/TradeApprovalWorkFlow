import pytest
from tests.fixture import Fixture
from trading_approval_process.application.commands.send_to_execute_command import SendToExecuteCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import InvalidTransitionException, AuthorizationException
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_state import TradeState


class TestSendToExecuteCommand:

    async def test_rejects_invalid_state_transition_from_draft(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = SendToExecuteCommand(fixture.executor_mock, fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
            await cmd.run(fixture.none_requester, trade.trade_id, token)

    async def test_rejects_unauthorized_requester_from_approved(self):
        fixture = Fixture()
        trade = fixture.build_valid_approved_from_pending_approval()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = SendToExecuteCommand(fixture.executor_mock, fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        # requester (creator) should not be allowed to send to execute
        with pytest.raises(AuthorizationException):
            await cmd.run(fixture.requester, trade.trade_id, token)

    async def test_send_to_execute_from_approved_by_approver_moves_to_sent_to_counterparty(self):
        fixture = Fixture()
        trade = fixture.build_valid_approved_from_pending_approval()
        fixture.repo_mock.get_by_id.return_value = trade
        fake_receipt = fixture.build_execution_receipt()
        fixture.executor_mock.send.return_value = fake_receipt
        cmd = SendToExecuteCommand(fixture.executor_mock, fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert updated_trade.state_before == TradeState.APPROVED
        assert updated_trade.state == TradeState.SENT_TO_COUNTERPARTY
        assert isinstance(updated_trade.execution_receipt, type(fake_receipt))
        assert updated_trade.execution_receipt.ticket_id == "TICKET12345"
        assert updated_trade.execution_receipt.status == "SENT"

    async def test_version_increment(self):
        fixture = Fixture()
        trade = fixture.build_valid_approved_from_pending_approval()
        version = trade.version
        fixture.repo_mock.get_by_id.return_value = trade
        fake_receipt = fixture.build_execution_receipt()
        fixture.executor_mock.send.return_value = fake_receipt
        cmd = SendToExecuteCommand(fixture.executor_mock, fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert updated_trade.version == version + 1

    async def test_audit_trail(self):
        fixture = Fixture()
        trade = fixture.build_valid_approved_from_pending_approval()
        fixture.repo_mock.get_by_id.return_value = trade
        fake_receipt = fixture.build_execution_receipt()
        fixture.executor_mock.send.return_value = fake_receipt
        cmd = SendToExecuteCommand(fixture.executor_mock, fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, token)

        assert len(updated_trade.audit) >= 1
        record = updated_trade.audit[-1]
        assert record.action == TradeAction.SEND_TO_EXECUTE
        assert record.user_id == fixture.none_requester
        assert record.state_before == TradeState.APPROVED
        assert record.state_after == TradeState.SENT_TO_COUNTERPARTY
        assert record.timestamp == fixture.fixed_now
