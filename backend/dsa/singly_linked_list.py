"""CHALLENGE B: replace flat storage with a real singly linked list.

This file already RUNS, using an ordinary Python list. It is deliberately not
the completed node implementation. The Workflow page calls these methods.

Build the structure with Node, head, tail and next. Maintain a cached _size.
Do not keep a Python list/dictionary/deque as the backing store. A temporary
result list inside to_list() is allowed. Match the public contracts below.

Indices are zero-based integers. Negative indices are invalid. Search/remove
uses the first matching value. See lecture slides 21-39 and 46-52.
"""


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


def require_integer(index):
    """Shared input contract; bool is not a usable position."""
    if not isinstance(index, int) or isinstance(index, bool):
        raise TypeError("Index must be an integer.")


class SinglyLinkedList:
    def __init__(self, items=None):
        # TODO B1: initialize head, tail, _size and load values using nodes.
        self.head = None
        self.tail = None
        self._items = list(items) if items is not None else []

    def prepend(self, value):
        # TODO B2: connect a new node before head. Handle an empty structure.
        self._items.insert(0, value)

    def append(self, value):
        # TODO B3: connect a new node after tail in O(1).
        self._items.append(value)

    def insert_at(self, index, value):
        """Insert at 0 <= index <= size. Raise IndexError otherwise."""
        require_integer(index)
        if not 0 <= index <= self.size():
            raise IndexError(index)
        # TODO B4: find the predecessor, then rewire its next link.
        self._items.insert(index, value)

    def remove_at(self, index):
        """Remove and return the value at 0 <= index < size."""
        require_integer(index)
        if not 0 <= index < self.size():
            raise IndexError(index)
        # TODO B5: update head/tail correctly, including the sole-node case.
        return self._items.pop(index)

    def remove(self, value):
        """Remove the first match and return True; return False if missing."""
        # TODO B6: search nodes and unlink only the first match.
        if value not in self._items:
            return False
        self._items.remove(value)
        return True

    def get(self, index):
        require_integer(index)
        if not 0 <= index < self.size():
            raise IndexError(index)
        # TODO B7: walk forward from head without changing links.
        return self._items[index]

    def index_of(self, value):
        """Return the first matching index, or -1 if missing."""
        # TODO B8: compare data while following next.
        return self._items.index(value) if value in self._items else -1

    def size(self):
        # TODO B9: return the cached node count in O(1).
        return len(self._items)

    def is_empty(self):
        return self.size() == 0

    def to_list(self):
        """Return a fresh display/storage snapshot, head to tail."""
        # TODO B10: traverse nodes until None. A result list is allowed here.
        return list(self._items)
