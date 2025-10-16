"""
Domain exceptions — enforce business invariants and validation rules.
"""
from .validation_exception import ValidationException
from .authorization_exception import AuthorizationException
from .invalid_transition_exception import InvalidTransitionException
from .not_found_exception import NotFoundException

__all__ = [
    "ValidationException",
    "AuthorizationException",
    "InvalidTransitionException",
    "NotFoundException",
]
