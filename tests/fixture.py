from datetime import date, timedelta, datetime
from dataclasses import replace
from unittest.mock import Mock, AsyncMock

from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider
from trading_approval_process.application.interfaces.i_trade_executor import ITradeExecutor
from trading_approval_process.application.interfaces.i_trade_repository import ITradeRepository
from trading_approval_process.domain.models.trade_details import TradeDetails
from trading_approval_process.domain.models.trade_action import  TradeAction
from trading_approval_process.domain.models.trade import Trade
from trading_approval_process.domain.models.execution_confirmation import ExecutionConfirmation
from trading_approval_process.domain.models.execution_receipt import ExecutionReceipt
from trading_approval_process.domain.models.trade_direction import TradeDirection
from trading_approval_process.domain.models.trade_style import TradeStyle


class Fixture:
    def __init__(self):
        # Fixed time for deterministic tests
        self.fixed_now = datetime(2025, 1, 2, 3, 4, 5)

        # Mocks
        self.repo_mock = AsyncMock(spec=ITradeRepository)
        self.time_mock = Mock(spec=ITimeProvider)
        self.executor_mock = AsyncMock(spec=ITradeExecutor)

        # Default users
        self.requester = "requester"
        self.none_requester = "noneRequester"

        # Configure mocks
        self.repo_mock.add.side_effect = lambda trade, token=None: trade
        self.time_mock.now.return_value = self.fixed_now

    def clear(self):
        self.repo_mock.reset_mock()
        self.time_mock.reset_mock()
        self.executor_mock.reset_mock()

    # ---- Builders ----

    def build_valid_details(self):
        return TradeDetails(
            trading_entity="BankA",
            counterparty="BankB",
            direction=TradeDirection.BUY,
            style=TradeStyle.FORWARD,
            notional_currency="USD",
            notional_amount=1_000_000,
            underlying="USD/EUR",
            trade_date=date.today(),
            value_date=date.today() + timedelta(days=2),
            delivery_date=date.today() + timedelta(days=5),
        )

    def build_invalid_details(self):
        return TradeDetails(
            trading_entity="BankA",
            counterparty="BankB",
            direction=TradeDirection.BUY,
            style=TradeStyle.FORWARD,
            notional_currency="USD",
            notional_amount=1_000_000,
            underlying="USD/EUR",
            trade_date=date.today(),
            value_date=date.today() - timedelta(days=2),
            delivery_date=date.today() - timedelta(days=5),
        )

    def build_valid_init_trade(self):
        return Trade()

    def build_valid_draft_trade(self):
        trade = self.build_valid_init_trade()
        trade.requester = self.requester
        trade.details = self.build_valid_details()
        trade.change(self.requester, TradeAction.CREATE, self.time_mock.now())
        return trade

    def build_valid_pending_approval(self):
        trade = self.build_valid_draft_trade()
        trade.change(self.requester, TradeAction.SUBMIT, self.time_mock.now())
        assert trade.state.name == "PENDING_APPROVAL", f"Expected PENDING_APPROVAL, got {trade.state}"
        return trade

    def build_valid_needs_reapproval(self):
        trade = self.build_valid_pending_approval()
        trade.details = replace(self.build_valid_details(), notional_amount=2_000_000)
        trade.change(self.none_requester, TradeAction.UPDATE, self.time_mock.now())
        return trade

    def build_valid_approved_from_pending_approval(self):
        trade = self.build_valid_pending_approval()
        trade.approver = self.none_requester
        trade.change(self.none_requester, TradeAction.APPROVE, self.time_mock.now())
        return trade

    def build_valid_sent_to_counterparty(self):
        trade = self.build_valid_approved_from_pending_approval()
        trade.execution_receipt = self.build_execution_receipt()
        trade.change(self.none_requester, TradeAction.SEND_TO_EXECUTE, self.time_mock.now())
        return trade

    def build_valid_executed(self):
        trade = self.build_valid_sent_to_counterparty()
        trade.execution_confirmation = self.build_execution_confirmation(trade)
        trade.details = replace(
            trade.details,
            strike=trade.execution_confirmation.strike,
            confirmation_id=trade.execution_confirmation.confirmation_id,
        )
        trade.change(self.requester, TradeAction.BOOK, self.time_mock.now())
        return trade

    def build_valid_cancelled(self):
        trade = self.build_valid_draft_trade()
        trade.change(self.requester, TradeAction.CANCEL, self.time_mock.now())
        return trade

    def build_execution_confirmation(self, trade):
        ticket_id = None
        if trade.execution_receipt:
            ticket_id = trade.execution_receipt.ticket_id
        return ExecutionConfirmation(
            ticket_id=ticket_id or "TICKET12345",
            confirmation_id="CONF12345",
            counterparty=trade.details.counterparty,
            strike=1.2345,
            timestamp=self.fixed_now,
        )

    def build_execution_receipt(self):
        return ExecutionReceipt(
            ticket_id="TICKET12345",
            sent_at=self.fixed_now,
            venue="ELECTRONIC",
            status="SENT",
            notes="Sent via FIX",
        )

    def build_invalid_details_wrong_dates(self):
        """TradeDate > ValueDate to trigger validation failure"""
        return TradeDetails(
            trading_entity="BankA",
            counterparty="BankB",
            direction=TradeDirection.BUY,
            style=TradeStyle.FORWARD,
            notional_currency="USD",
            notional_amount=1_000_000,
            underlying="USD/EUR",
            trade_date=self.fixed_now.date() + timedelta(days=5),
            value_date=self.fixed_now.date(),
            delivery_date=self.fixed_now.date() + timedelta(days=1),
        )
