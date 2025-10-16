from .domain_exception import DomainException

class ValidationException(DomainException):
    code = "TRADE_VALIDATION_ERROR"
