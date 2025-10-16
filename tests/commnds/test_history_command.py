from tests.fixture import Fixture
from trading_approval_process.application.commands.history_command import HistoryCommand
from trading_approval_process.core.cancellation_token import CancellationToken


class TestHistoryCommand:
    async def test_history_returns_audit_trail(self):
        # Arrange
        fixture = Fixture()
        trade = fixture.build_valid_approved_from_pending_approval()
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = HistoryCommand(fixture.repo_mock)
        token = CancellationToken()

        # Act
        history = await cmd.run(trade.trade_id, token)

        # Assert
        assert history.trade_id == trade.trade_id
        assert len(history.records) > 0
        assert history.records[0].user_id in (fixture.requester, fixture.none_requester)
