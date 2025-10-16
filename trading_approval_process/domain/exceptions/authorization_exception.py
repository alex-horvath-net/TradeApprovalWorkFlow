from .domain_exception import DomainException


class AuthorizationException(DomainException):
    code = "TRADE_AUTHORIZATION_FAILED"
