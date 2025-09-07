from typing import Protocol, runtime_checkable


@runtime_checkable
class CounterProtocol(Protocol):
    """Protocol for a counter that can be incremented, decremented, and reset."""

    def get_count(self) -> int:
        """
        Returns the current count.

        Returns:
            int: The current count.
        """
        ...

    def increment(self) -> None:
        """Increments the count by one."""
        ...

    def decrement(self) -> None:
        """
        Decrements the count by one.

        Raises:
            ValueError: If the count is already zero.
        """
        ...

    def reset(self) -> None:
        """Resets the count to zero."""
        ...
