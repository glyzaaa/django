import unittest
from django.urls import reverse
from backend.dsa.queue import ServiceQueue
from tests.helpers import WorkspaceCase


class QueueGoalTests(unittest.TestCase):
    def test_01_first_arrival_leaves_first(self):
        queue=ServiceQueue([3,1,4,3,2])
        self.assertEqual([queue.dequeue() for _ in range(5)],[3,1,4,3,2],"FIFO must remove the earliest waiting arrival first.")

    def test_02_peek_reads_front_without_mutation(self):
        queue=ServiceQueue(["A","B","C"])
        for _ in range(3):self.assertEqual(queue.peek(),"A","peek() must read the FIFO front.")
        self.assertEqual(queue.to_list(),["A","B","C"])
        self.assertEqual(queue.size(),3)

    def test_03_mixed_arrivals_and_removals(self):
        queue=ServiceQueue();queue.enqueue("A");queue.enqueue("B")
        self.assertEqual(queue.dequeue(),"A")
        queue.enqueue("C")
        self.assertEqual(queue.to_list(),["B","C"])
        self.assertEqual(queue.dequeue(),"B");self.assertEqual(queue.dequeue(),"C")

    def test_04_empty_operations_raise(self):
        queue=ServiceQueue()
        self.assertTrue(queue.is_empty());self.assertEqual(queue.size(),0)
        with self.assertRaises(IndexError):queue.dequeue()
        with self.assertRaises(IndexError):queue.peek()

    def test_05_single_item_and_reuse(self):
        queue=ServiceQueue();queue.enqueue(7)
        self.assertEqual(queue.peek(),7);self.assertEqual(queue.dequeue(),7)
        queue.enqueue(9);self.assertEqual(queue.dequeue(),9);self.assertTrue(queue.is_empty())

    def test_06_snapshot_reload_preserves_fifo(self):
        queue=ServiceQueue(["A","B","C"])
        self.assertEqual(queue.dequeue(),"A")
        reloaded=ServiceQueue(queue.to_list());reloaded.enqueue("D")
        self.assertEqual([reloaded.dequeue() for _ in range(3)],["B","C","D"])

    def test_07_constructor_and_snapshot_are_independent(self):
        values=["A","B"];queue=ServiceQueue(values);values.reverse()
        self.assertEqual(queue.to_list(),["A","B"])
        snapshot=queue.to_list();snapshot.append("C")
        self.assertEqual(queue.size(),2)

    def test_08_duplicates_keep_arrival_positions(self):
        queue=ServiceQueue([5,5,8])
        self.assertEqual([queue.dequeue() for _ in range(3)],[5,5,8])


class QueueWebsiteGoalTests(WorkspaceCase):
    def test_09_real_serve_route_is_fifo_after_refreshes(self):
        a,b,c=[self.item(x) for x in ["Queue A","Queue B","Queue C"]]
        for item in [a,b,c]:self.join(item)
        for expected in [a,b,c]:
            state=self.client.get("/api/state/").json()
            self.assertEqual(state["queue"]["selected_next"],expected.id,"The browser's backend selection must be FIFO, not just the displayed card order.")
            self.client.post(reverse("workspace:queue_serve"))
            expected.refresh_from_db();self.assertEqual(expected.status,"doing")
            self.assertEqual(self.workspace.events.filter(kind="served").latest("id").details["item_id"],expected.id)
        self.assertEqual(self.fresh().queue_state,[])

    def test_10_saved_state_can_be_reconstructed_between_operations(self):
        a,b=self.item("A"),self.item("B")
        self.join(a);self.join(b)
        self.client.post(reverse("workspace:queue_serve"))
        self.assertEqual(self.fresh().queue_state,[b.id])
        self.assertEqual(self.client.get("/api/state/").json()["queue"]["selected_next"],b.id)
