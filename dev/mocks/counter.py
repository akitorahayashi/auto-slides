from src.procotols.counter import CounterProtocol


class MockCounter(CounterProtocol):
    """A mock counter for testing purposes with call tracking."""

    _count: int
    increment_call_count: int
    decrement_call_count: int
    reset_call_count: int

    def __init__(self, initial_count: int = 0):
        if initial_count < 0:
            raise ValueError("Initial count cannot be negative.")
        self._count = initial_count
        self.increment_call_count = 0
        self.decrement_call_count = 0
        self.reset_call_count = 0

    def get_count(self) -> int:
        """Returns the current count."""
        return self._count

    def increment(self) -> None:
        """Increments the count and tracks the call."""
        self._count += 1
        self.increment_call_count += 1

    def decrement(self) -> None:
        """Decrements the count and tracks the call."""
        self.decrement_call_count += 1
        if self._count <= 0:
            raise ValueError("Count cannot go below zero.")
        self._count -= 1

    def reset(self) -> None:
        """Resets the count and tracks the call."""
        self._count = 0
        self.reset_call_count += 1


# Statically verify that MockCounter implements the protocol.
_: CounterProtocol = MockCounter()
