from src.procotols.counter import CounterProtocol


class Counter:
    """A simple counter that implements CounterProtocol."""

    _count: int

    def __init__(self, initial_count: int = 0):
        if initial_count < 0:
            raise ValueError("Initial count cannot be negative.")
        self._count = initial_count

    def get_count(self) -> int:
        """Returns the current count."""
        return self._count

    def increment(self) -> None:
        """Increments the count by one."""
        self._count += 1

    def decrement(self) -> None:
        """
        Decrements the count by one.

        Raises:
            ValueError: If the count is already zero.
        """
        if self._count <= 0:
            raise ValueError("Count cannot be negative.")
        self._count -= 1

    def reset(self) -> None:
        """Resets the count to its initial value."""
        self._count = 0


# Statically verify that Counter implements the protocol.
_: CounterProtocol = Counter()
