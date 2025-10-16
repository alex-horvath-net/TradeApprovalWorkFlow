from datetime import datetime, timezone

from trading_approval_process.application.interfaces.i_time_provider import ITimeProvider


class SystemTime(ITimeProvider):
    """System clock provider (UTC)."""

    def now(self) -> datetime:
        """Return the current UTC datetime, precise to microseconds."""
        return datetime.now(timezone.utc)
