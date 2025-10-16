import pytest
from tests.fixture import Fixture
from trading_approval_process.application.commands.update_command import UpdateCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import *
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_state import TradeState


class TestUpdateCommand:

    async def test_rejects_invalid_details_in_draft_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        invalid_details = fixture.build_invalid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(ValidationException):
            await cmd.run(fixture.requester, trade.trade_id, invalid_details, token)

    async def test_rejects_invalid_details_in_pending_approval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        invalid_details = fixture.build_invalid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(ValidationException):
            await cmd.run(fixture.none_requester, trade.trade_id, invalid_details, token)

    async def test_rejects_invalid_state_transition(self):
        fixture = Fixture()
        trade = fixture.build_valid_init_trade()
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(InvalidTransitionException):
            await cmd.run(fixture.requester, trade.trade_id, details, token)

    async def test_rejects_the_unauthorized_none_requester_in_draft_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(AuthorizationException):
            await cmd.run(fixture.none_requester, trade.trade_id, details, token)

    async def test_rejects_the_unauthorized_requester_in_pending_approval_state(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(AuthorizationException):
            await cmd.run(fixture.requester, trade.trade_id, details, token)

    async def test_accept_requester_for_valid_state_transition_from_draft(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, details, token)

        assert updated_trade.state_before == TradeState.DRAFT
        assert updated_trade.state == TradeState.DRAFT

    async def test_accept_none_requester_for_state_transition_from_pending_approval(self):
        fixture = Fixture()
        trade = fixture.build_valid_pending_approval()
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.none_requester, trade.trade_id, details, token)

        assert updated_trade.state_before == TradeState.PENDING_APPROVAL
        assert updated_trade.state == TradeState.NEEDS_REAPPROVAL

    async def test_version_increment(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        version = trade.version
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, details, token)

        assert updated_trade.version == version + 1  # Version should increment by 1

    async def test_audit_trail(self):
        fixture = Fixture()
        trade = fixture.build_valid_draft_trade()
        details = fixture.build_valid_details()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = UpdateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        updated_trade = await cmd.run(fixture.requester, trade.trade_id, details, token)

        assert len(updated_trade.audit) >= 1
        record = updated_trade.audit[-1]
        assert record.action == TradeAction.UPDATE
        assert record.user_id == fixture.requester
        assert record.state_before == TradeState.DRAFT
        assert record.state_after == TradeState.DRAFT
        assert record.timestamp == fixture.fixed_now
        assert record.details == trade.details
