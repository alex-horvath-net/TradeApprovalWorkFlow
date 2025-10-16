import pytest
from tests.fixture import Fixture
from trading_approval_process.application.commands.create_command import CreateCommand
from trading_approval_process.core.cancellation_token import CancellationToken
from trading_approval_process.domain.exceptions import ValidationException
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_state import TradeState


class TestCreateCommand:
    async def test_everyone_can_create_valid_trade(self):
        fixture = Fixture()
        details = fixture.build_valid_details()
        cmd = CreateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        trade = await cmd.run("random_user", details, token)

        assert trade.requester == "random_user"
        assert trade.details == details
        assert trade.state_before == TradeState.INITIAL
        assert trade.state == TradeState.DRAFT

    async def test_no_one_can_create_trade_with_invalid_details(self):
        fixture = Fixture()
        details = fixture.build_invalid_details_wrong_dates()
        cmd = CreateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        with pytest.raises(ValidationException) as ex:
            await cmd.run(fixture.requester, details, token)

        assert "TradeDate" in str(ex.value) or "ValueDate" in str(ex.value)

    async def test_version_increment(self):
        fixture = Fixture()
        details = fixture.build_valid_details()
        cmd = CreateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        trade = await cmd.run(fixture.requester, details, token)

        assert trade.version == 1

    async def test_audit_trail(self):
        fixture = Fixture()
        details = fixture.build_valid_details()
        cmd = CreateCommand(fixture.repo_mock, fixture.time_mock)
        token = CancellationToken()

        trade = await cmd.run(fixture.requester, details, token)

        assert len(trade.audit) == 1
        record = trade.audit[0]
        assert record.step == 1
        assert record.action == TradeAction.CREATE
        assert record.user_id == fixture.requester
        assert record.state_before == TradeState.INITIAL
        assert record.state_after == TradeState.DRAFT
        assert record.notes == "Trade created"
        assert record.timestamp == fixture.fixed_now, f"Expected {fixture.fixed_now}, got {record.timestamp}"
        assert record.details == details