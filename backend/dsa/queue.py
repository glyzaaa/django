from collections import deque


class ServiceQueue:
    def __init__(self, items=None):
        """Load existing values in arrival order."""
        self._items = deque(items) if items is not None else deque()

    def enqueue(self, value):
        """Add a request at the rear."""
        self._items.append(value)

    def dequeue(self):
        """Remove and return the earliest waiting request."""
        if self.is_empty():
            raise IndexError("The service queue is empty.")

        return self._items.popleft()

    def peek(self):
        """Read the next request without removing it."""
        if self.is_empty():
            raise IndexError("The service queue is empty.")

        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def to_list(self):
        """Return a fresh arrival-order snapshot for SQLite persistence."""
        return list(self._items)
