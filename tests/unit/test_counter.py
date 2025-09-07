import pytest

from src.models.counter import Counter
from src.procotols.counter import CounterProtocol


@pytest.fixture
def counter() -> Counter:
    """Returns a default Counter instance starting at 0."""
    return Counter()


class TestCounter:
    """Test suite for the Counter model."""

    def test_counter_initialization(self):
        """Tests that the counter initializes with a specific value."""
        c = Counter(initial_count=5)
        assert c.get_count() == 5

    def test_counter_default_initialization(self, counter: Counter):
        """Tests that the counter initializes to 0 by default."""
        assert counter.get_count() == 0

    def test_counter_negative_initialization(self):
        """Tests that initializing with a negative number raises an error."""
        with pytest.raises(ValueError, match="Initial count cannot be negative."):
            Counter(initial_count=-1)

    def test_counter_increment(self, counter: Counter):
        """Tests the increment method."""
        counter.increment()
        assert counter.get_count() == 1
        counter.increment()
        assert counter.get_count() == 2

    def test_counter_decrement(self):
        """Tests the decrement method from a specific starting count."""
        c = Counter(initial_count=2)
        c.decrement()
        assert c.get_count() == 1
        c.decrement()
        assert c.get_count() == 0

    def test_counter_decrement_error(self, counter: Counter):
        """Tests that decrementing at zero raises a ValueError."""
        with pytest.raises(ValueError, match="Count cannot be negative."):
            counter.decrement()

    def test_counter_reset(self):
        """Tests the reset method."""
        c = Counter(initial_count=5)
        c.increment()
        c.reset()
        assert c.get_count() == 0

    def test_counter_protocol(self, counter: Counter):
        """Tests that the Counter class fulfills the CounterProtocol."""
        assert isinstance(counter, CounterProtocol)
