import uuid
from dataclasses import fields
from datetime import datetime
from typing import Callable, Optional

from trading_approval_process.domain.exceptions import *
from trading_approval_process.domain.models.trade_state import TradeState
from trading_approval_process.domain.models.trade_action import TradeAction
from trading_approval_process.domain.models.trade_details import TradeDetails
from trading_approval_process.domain.models.audit_record import AuditRecord
from trading_approval_process.domain.models.execution_receipt import ExecutionReceipt
from trading_approval_process.domain.models.execution_confirmation import ExecutionConfirmation
from trading_approval_process.domain.models.trade_diff import TradeDiff
from trading_approval_process.domain.models.trade_history import TradeHistory
from trading_approval_process.domain.models.trade_state_transitions import StateTransitions


class Trade:
    """Domain aggregate representing a Trade."""

    def __init__(self,  trade_id: uuid.UUID | None = None, logger: Optional[Callable[[str], None]] = None) -> None:
        self._logger = logger
        self.trade_id = trade_id or uuid.uuid4()
        self.requester: str | None = None
        self.approver: str | None = None
        self.state: TradeState = TradeState.INITIAL
        self.state_before: TradeState = TradeState.INITIAL
        self.version: int = 0
        self.details: TradeDetails | None = None
        self.audit: list[AuditRecord] = []
        self.execution_receipt: ExecutionReceipt | None = None
        self.execution_confirmation: ExecutionConfirmation | None = None

        self._transitions = StateTransitions()

    def validate(self, user: str, action: TradeAction, new_details: TradeDetails | None = None ) -> None:
        """Validate that the given user may perform the action in the current state."""

        if not self._transitions.is_state_registered(self.state):
            raise InvalidTransitionException(f"State '{self.state.name}' is not registered in transition map.")

        if not self._transitions.is_action_available(self.state, action):
            raise InvalidTransitionException(f"Action '{action.name}' is not allowed from state '{self.state.name}'.")

        if not self._transitions.is_user_authorized(self, user, action):
            raise AuthorizationException(
                f"User '{user}' is not authorised to perform action '{action.name}' from state '{self.state.name}'.")

        # Validate trade details (data-level correctness)
        if new_details is not None:
            new_details.validate()

    def change(self, user: str, action: TradeAction, timestamp: datetime) -> None:
        next_state, note = self._transitions.get_transition(self.state, action)

        self.version += 1
        self.state_before = self.state
        self.state = next_state
        self.audit.append(
            AuditRecord(self.version, action, user, self.state_before, self.state, self.details, timestamp, note))


        if self._logger:
            self._logger(
                f"[Trade {self.trade_id}] {action.name} by {user} → {self.state.name} at {timestamp.isoformat()}")

    def to_history(self) -> TradeHistory:
        """"Retrieve full history ot the trade."""
        return TradeHistory(self.trade_id, self.requester, self.approver, self.audit)

    def get_differences(self, version_a: int, version_b: int) -> TradeDiff:
        """Compute field-level differences between two TradeDetails instances."""

        details_a = self._get_details_by_version(version_a)
        details_b = self._get_details_by_version(version_b)

        differences = {}
        for field in fields(details_a):
            field_in_details_a = getattr(details_a, field.name)
            field_in_details_b = getattr(details_b, field.name)
            if field_in_details_a != field_in_details_b:
                differences[field.name] = ( str(field_in_details_a), str(field_in_details_b) )

        return TradeDiff(differences)

    def _get_details_by_version(self, version: int) -> TradeDetails:
        """Retrieve details related to the given version."""

        if version == self.version:
            return self.details

        for record in self.audit:
            if record.step == version:
                return record.details

        raise NotFoundException(f"Version {version} not found for trade {self.trade_id}.")
