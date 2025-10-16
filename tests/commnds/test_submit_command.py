import pytest
from tests.fixture import Fixture
from trading_approval_process.application.commands.submit_command import SubmitCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import InvalidTransitionException, AuthorizationException
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_state import TradeState


class TestSubmitCommand:
    async def test_rejects_invalid_state_transition(self):
        fixture = Fixture()
        init_trade = fixture.build_valid_init_trade()
        fixture.repo_mock.get_by_id.return_value = init_trade
        cmd = SubmitCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
            await cmd.run(fixture.requester, init_trade.trade_id, token)

    async def test_rejects_unauthorized_user(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = SubmitCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(AuthorizationException):
            await cmd.run(fixture.none_requester, trade.trade_id, token)

    async def test_version_increment(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        version = trade.version
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = SubmitCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert updated_trade.version == version + 1 # Version should increment by 1

    async def test_audit_trail(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = SubmitCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, token)

        assert len(updated_trade.audit) >= 1
        record = updated_trade.audit[-1]
        assert record.action == TradeAction.SUBMIT
        assert record.user_id == fixture.requester
        assert record.state_before == TradeState.DRAFT
        assert record.state_after == TradeState.PENDING_APPROVAL
        assert record.timestamp == fixture.fixed_now
        assert record.details == trade.details
