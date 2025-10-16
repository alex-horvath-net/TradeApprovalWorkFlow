from .domain_exception import DomainException

class InvalidTransitionException(DomainException):
    code = "TRADE_INVALID_TRANSITION"
