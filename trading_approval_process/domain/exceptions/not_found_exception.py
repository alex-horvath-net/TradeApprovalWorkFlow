from .domain_exception import DomainException

class NotFoundException(DomainException):
    code = "TRADE_NOT_FOUND"