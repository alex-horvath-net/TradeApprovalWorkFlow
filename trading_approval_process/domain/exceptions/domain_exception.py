
class DomainException(Exception):
    """Base class for all domain-level exceptions."""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str):
        super().__init__(f"[{self.code}] {message}")