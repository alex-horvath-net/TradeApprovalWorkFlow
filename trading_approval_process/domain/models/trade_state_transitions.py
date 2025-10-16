from types import MappingProxyType
from typing import Tuple, Callable, Any

from trading_approval_process.domain.models.trade_state import TradeState
from trading_approval_process.domain.models.trade_action import TradeAction


class StateTransitions:

    def __init__(self) -> None:

        # Allowed state transitions: from_state : action : [to_state, nore, user_right]
        self._map_state_translations: MappingProxyType[TradeState, dict[TradeAction, Tuple[ TradeState, str, Callable[[Any, str], bool]]]] = MappingProxyType({
            TradeState.INITIAL: {
                TradeAction.CREATE: (TradeState.DRAFT, "Trade created", lambda trade, user: True) },
            TradeState.DRAFT: {
                TradeAction.UPDATE: (TradeState.DRAFT, "Trade updated", lambda trade, user: user in [trade.requester]) ,
                TradeAction.CANCEL: (TradeState.CANCELLED, "Trade cancelled", lambda trade, user: user in [trade.requester]) ,
                TradeAction.SUBMIT: (TradeState.PENDING_APPROVAL, "Trade submitted", lambda trade, user: user in [trade.requester]) , },
            TradeState.PENDING_APPROVAL: {
                TradeAction.UPDATE: (TradeState.NEEDS_REAPPROVAL, "Trade updated, need reapproval", lambda trade, user: user not in [trade.requester]) ,
                TradeAction.CANCEL: (TradeState.CANCELLED, "Trade cancelled", lambda trade, user: user not in [trade.requester]) ,
                TradeAction.APPROVE: (TradeState.APPROVED, "Trade approved", lambda trade, user: user not in [trade.requester]) ,},
            TradeState.NEEDS_REAPPROVAL: {
                TradeAction.APPROVE: (TradeState.APPROVED, "Trade reapproved", lambda trade, user: user in [trade.requester]),
                TradeAction.CANCEL: (TradeState.CANCELLED, "Trade cancelled", lambda trade, user: user in [trade.requester]) },
            TradeState.APPROVED: {
                TradeAction.SEND_TO_EXECUTE: (TradeState.SENT_TO_COUNTERPARTY, "Trade sent to counterparty", lambda trade, user: user in [trade.approver] ),
                TradeAction.CANCEL: (TradeState.CANCELLED, "Trade cancelled",  lambda trade, user: user in [trade.approver] ) },
            TradeState.SENT_TO_COUNTERPARTY: {
                TradeAction.BOOK: (TradeState.EXECUTED, "Trade executed", lambda trade, user: user in [trade.requester, trade.approver] ),
                TradeAction.CANCEL: (TradeState.CANCELLED, "Trade cancelled", lambda trade, user: user in [trade.requester, trade.approver]) },
            #TradeState.CANCEL_REQUESTED: {
            #    TradeAction.CANCEL_CONFIRMED: TradeState.CANCELLED,
            #    TradeAction.EXECUTION_CONFIRMED: TradeState.EXECUTED,
            #},
            TradeState.EXECUTED: [],
            TradeState.CANCELLED: [],
        })

    def is_state_registered(self, state: TradeState) -> bool:
        """Is the given state registered in the current state?"""
        return state in self._map_state_translations

    def is_action_available(self, state: TradeState, action: TradeAction) -> bool:
        """Is the given action available in the current state?"""
        available_actions = self._map_state_translations[state]
        return action in available_actions

    def is_user_authorized(self, trade: Any, user: str, action: TradeAction) -> bool:
        """Is the given user authorized in the current state for the given action?"""
        next_state, note, is_authorised = self._map_state_translations[trade.state][action]
        return is_authorised(trade, user)

    def get_transition(self, state: TradeState, action: TradeAction) -> tuple[TradeState, str]  :
        """Get the transition from the given state by given action."""
        next_state, note, is_authorised = self._map_state_translations[state][action]
        return (next_state, note)
