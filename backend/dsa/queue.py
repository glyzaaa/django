"""CHALLENGE A: change the runnable baseline into a FIFO queue.

The Service queue page calls this class. Currently the newest waiting request
leaves first. Fix dequeue AND peek so the earliest waiting request leaves first.

Keep the class and method names. to_list() must return a NEW list in arrival
order, earliest to latest, because Django saves it and reloads it next request.
Use an efficient representation for O(1) enqueue and dequeue.
See docs/STUDENT_ACTIVITY.md and lecture slides 3-20.
"""


class ServiceQueue:
    def __init__(self, items=None):
        # TODO A1: choose a representation with efficient FIFO end operations.
        self._items = list(items) if items is not None else []

    def enqueue(self, value):
        """Add a request at the rear."""
        self._items.append(value)

    def dequeue(self):
        """Remove and return the next request. Baseline selects the newest."""
        if self.is_empty():
            raise IndexError("The service queue is empty.")
        # TODO A2: select the FRONT while preserving the remaining arrival order.
        return self._items.pop()

    def peek(self):
        """Read the next request without removal."""
        if self.is_empty():
            raise IndexError("The service queue is empty.")
        # TODO A3: this must agree with dequeue and leave the queue unchanged.
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def to_list(self):
        """Return a fresh arrival-order snapshot for SQLite persistence."""
        return list(self._items)
