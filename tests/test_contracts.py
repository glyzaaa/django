import unittest
from backend.dsa.queue import ServiceQueue
from backend.dsa.singly_linked_list import SinglyLinkedList


class PublicContractTests(unittest.TestCase):
    """Website-compatible contracts, independent of the unfinished goals."""
    def test_queue_empty_errors_and_constructor_copy(self):
        values=[1,2];queue=ServiceQueue(values);values.append(3)
        self.assertEqual(queue.to_list(),[1,2])
        snapshot=queue.to_list();snapshot.clear()
        self.assertEqual(queue.size(),2)
        queue.dequeue();queue.dequeue()
        self.assertTrue(queue.is_empty())
        for operation in [queue.dequeue,queue.peek]:
            with self.assertRaises(IndexError):operation()

    def test_linked_public_operations_and_bounds(self):
        linked=SinglyLinkedList([10,20,30])
        linked.prepend(5);linked.insert_at(2,15)
        self.assertEqual(linked.remove_at(3),20)
        self.assertEqual(linked.to_list(),[5,10,15,30])
        self.assertEqual(linked.index_of(30),3)
        self.assertEqual(linked.get(2),15)
        self.assertFalse(linked.remove(99))
        self.assertTrue(linked.remove(10))
        self.assertEqual(linked.to_list(),[5,15,30])
        for index in [-1,3,999]:
            for method in [linked.get,linked.remove_at]:
                with self.assertRaises(IndexError):method(index)
        with self.assertRaises(IndexError):linked.insert_at(4,1)

    def test_linked_storage_snapshot_is_a_copy(self):
        values=[1,2];linked=SinglyLinkedList(values);values.append(3)
        result=linked.to_list();result.clear()
        self.assertEqual(linked.to_list(),[1,2])
