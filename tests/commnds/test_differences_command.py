from tests.fixture import Fixture
from trading_approval_process.application.commands.differences_command import DifferencesCommand
from trading_approval_process.core.cancellation_token import CancellationToken


class TestDifferencesCommand:

    async def test_differences_between_two_versions(self):
        fixture = Fixture()
        trade = fixture.build_valid_needs_reapproval()
        last_version = trade.audit[-1].step
        before_last_version = trade.audit[-2].step
        fixture.repo_mock.get_by_id.return_value = trade
        cmd = DifferencesCommand(fixture.repo_mock)
        token = CancellationToken()

        diff = await cmd.run( trade.trade_id, before_last_version, last_version, token )

        print("DIFF CHANGES:", diff.changes)

        assert "notional_amount" in diff.changes
        before, after = diff.changes["notional_amount"]
        assert before == str(1_000_000)
        assert after == str(2_000_000)
