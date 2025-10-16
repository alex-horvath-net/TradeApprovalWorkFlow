import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional


class CancellationToken:
    """
    Cooperative cancellation primitive for async workflows.

    Inspired by .NET's CancellationToken:
    - Allows multiple consumers to cooperatively cancel long-running tasks.
    - Safe to share across coroutines.
    - Lightweight, thread-safe, and instrumentation-friendly.
    """

    __slots__ = ("_event", "_cancel_message")

    def __init__(self) -> None:
        self._event = asyncio.Event()
        self._cancel_message: Optional[str] = None

    # ---------------------------
    # Core API
    # ---------------------------
    def cancel(self, message: Optional[str] = None) -> None:
        """Signal cancellation to all awaiting or polling tasks."""
        if not self._event.is_set():
            self._cancel_message = message or "Operation cancelled."
            self._event.set()
            logging.debug("CancellationToken: cancel() triggered — %s", self._cancel_message)

    def is_cancellation_requested(self) -> bool:
        """Return True if cancellation has been requested."""
        return self._event.is_set()

    async def throw_if_cancellation_requested(self) -> None:
        """Raise CancelledError cooperatively if cancellation requested."""
        if self._event.is_set():
            logging.debug("CancellationToken: throw_if_cancellation_requested() triggered.")
            raise asyncio.CancelledError(self._cancel_message or "Operation cancelled.")

    async def wait(self) -> None:
        """Block until cancellation is triggered. Used for graceful shutdowns."""
        await self._event.wait()

    # ---------------------------
    # Convenience / diagnostic
    # ---------------------------
    def __repr__(self) -> str:
        return f"<CancellationToken cancelled={self.is_cancellation_requested()} message={self._cancel_message!r}>"

    def __bool__(self) -> bool:
        """Allow direct boolean checks in if statements."""
        return self.is_cancellation_requested()


# ---------------------------
# Context manager helper
# ---------------------------
@asynccontextmanager
async def cancellation_scope(timeout: Optional[float] = None):
    """
    Context manager that yields a `CancellationToken` and cancels after a timeout.

    Example:
        async with cancellation_scope(5) as token:
            await long_running_operation(token)
    """
    token = CancellationToken()
    try:
        if timeout:
            async with asyncio.timeout(timeout):
                yield token
        else:
            yield token
    except asyncio.TimeoutError:
        token.cancel(f"Operation timed out after {timeout}s")
        raise asyncio.CancelledError(f"Operation timed out after {timeout}s")
