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
        """Initialize an empty linked list and load optional values."""
        self.head = None
        self.tail = None
        self._size = 0

        if items is not None:
            for value in items:
                self.append(value)

    def prepend(self, value):
        """Add a new node at the beginning in O(1)."""
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node

        if self.tail is None:
            self.tail = new_node

        self._size += 1

    def append(self, value):
        """Add a new node at the end in O(1)."""
        new_node = Node(value)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1

    def insert_at(self, index, value):
        """Insert at 0 <= index <= size."""
        require_integer(index)

        if not 0 <= index <= self._size:
            raise IndexError(index)

        if index == 0:
            self.prepend(value)
            return

        if index == self._size:
            self.append(value)
            return

        previous = self.head

        for _ in range(index - 1):
            previous = previous.next

        new_node = Node(value)
        new_node.next = previous.next
        previous.next = new_node

        self._size += 1

    def remove_at(self, index):
        """Remove and return the value at 0 <= index < size."""
        require_integer(index)

        if not 0 <= index < self._size:
            raise IndexError(index)

        if index == 0:
            removed_node = self.head
            self.head = self.head.next

            self._size -= 1

            if self._size == 0:
                self.tail = None

            return removed_node.data

        previous = self.head

        for _ in range(index - 1):
            previous = previous.next

        removed_node = previous.next
        previous.next = removed_node.next

        if removed_node is self.tail:
            self.tail = previous

        self._size -= 1

        return removed_node.data

    def remove(self, value):
        """Remove the first matching value."""
        current = self.head
        previous = None

        while current is not None:
            if current.data == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

                if current is self.tail:
                    self.tail = previous

                self._size -= 1
                return True

            previous = current
            current = current.next

        return False

    def get(self, index):
        """Return the value at the given index."""
        require_integer(index)

        if not 0 <= index < self._size:
            raise IndexError(index)

        current = self.head

        for _ in range(index):
            current = current.next

        return current.data

    def index_of(self, value):
        """Return the first matching index, or -1 if missing."""
        current = self.head
        index = 0

        while current is not None:
            if current.data == value:
                return index

            current = current.next
            index += 1

        return -1

    def size(self):
        """Return the cached node count in O(1)."""
        return self._size

    def is_empty(self):
        return self._size == 0

    def to_list(self):
        """Return a fresh list containing values from head to tail."""
        result = []
        current = self.head

        while current is not None:
            result.append(current.data)
            current = current.next

        return result
