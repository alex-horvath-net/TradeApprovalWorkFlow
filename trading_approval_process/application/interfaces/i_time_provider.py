from datetime import datetime
from abc import ABC, abstractmethod

class ITimeProvider(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Return the current UTC time."""
        pass
