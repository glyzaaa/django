import unittest
from collections import deque
from backend.dsa.singly_linked_list import Node, SinglyLinkedList
from tests.helpers import WorkspaceCase


class LinkedListGoalTests(unittest.TestCase):
    def nodes(self,linked,expected):
        node=getattr(linked,"head",None);nodes=[];seen=set()
        while node is not None:
            self.assertIsInstance(node,Node,"Every chain element must be a Node object.")
            self.assertNotIn(id(node),seen,"The last next must be None; cycles are invalid.")
            self.assertLess(len(nodes),len(expected)+1,"Too many reachable nodes.")
            seen.add(id(node));nodes.append(node);node=node.next
        self.assertEqual([n.data for n in nodes],expected,"Values must live in a reachable head/next chain, not only in a Python list.")
        self.assertEqual(linked.size(),len(expected))
        self.assertEqual(getattr(linked,"_size",None),len(expected),"Maintain a cached _size count.")
        self.assertIs(getattr(linked,"tail",None),nodes[-1] if nodes else None,"tail must refer to the final actual Node.")
        return nodes

    def test_01_node_has_data_and_next(self):
        node=Node("A");self.assertEqual(node.data,"A");self.assertIsNone(node.next)

    def test_02_public_insertion_sequence(self):
        linked=SinglyLinkedList();linked.append(10);linked.append(20);linked.prepend(5);linked.insert_at(2,15)
        self.assertEqual(linked.to_list(),[5,10,15,20])

    def test_03_get_search_and_first_duplicate(self):
        linked=SinglyLinkedList([10,20,20,30])
        self.assertEqual(linked.get(2),20);self.assertEqual(linked.index_of(20),1);self.assertEqual(linked.index_of(99),-1)
        self.assertEqual(linked.to_list(),[10,20,20,30])

    def test_04_remove_by_value_and_missing(self):
        linked=SinglyLinkedList([10,20,20,30])
        self.assertTrue(linked.remove(20));self.assertEqual(linked.to_list(),[10,20,30])
        self.assertFalse(linked.remove(99));self.assertEqual(linked.size(),3)

    def test_05_remove_at_returns_value(self):
        linked=SinglyLinkedList([10,20,30])
        self.assertEqual(linked.remove_at(1),20);self.assertEqual(linked.to_list(),[10,30])

    def test_06_invalid_bounds_preserve_state(self):
        linked=SinglyLinkedList([10,20])
        for method in [linked.get,linked.remove_at]:
            for index in [-1,2,99]:
                with self.assertRaises(IndexError):method(index)
        for index in [-1,3]:
            with self.assertRaises(IndexError):linked.insert_at(index,30)
        self.assertEqual(linked.to_list(),[10,20])

    def test_07_empty_read_remove_and_missing_value(self):
        linked=SinglyLinkedList()
        self.assertTrue(linked.is_empty());self.assertEqual(linked.to_list(),[])
        with self.assertRaises(IndexError):linked.get(0)
        with self.assertRaises(IndexError):linked.remove_at(0)
        self.assertFalse(linked.remove("missing"))

    def test_08_insert_at_size_appends(self):
        linked=SinglyLinkedList();linked.insert_at(0,"A");linked.insert_at(1,"B")
        self.assertEqual(linked.to_list(),["A","B"])

    def test_09_copies_are_independent(self):
        source=[1,2];linked=SinglyLinkedList(source);source.clear()
        result=linked.to_list();result.reverse();self.assertEqual(linked.to_list(),[1,2])

    def test_10_integer_positions_only(self):
        linked=SinglyLinkedList([1])
        for index in [True,"0",0.5]:
            with self.assertRaises(TypeError):linked.get(index)
            with self.assertRaises(TypeError):linked.remove_at(index)
            with self.assertRaises(TypeError):linked.insert_at(index,2)

    def test_11_constructor_builds_actual_nodes(self):
        self.nodes(SinglyLinkedList([10,20,30]),[10,20,30])

    def test_12_head_tail_updates_and_single_node_reuse(self):
        linked=SinglyLinkedList();self.nodes(linked,[])
        linked.append("A");self.nodes(linked,["A"])
        linked.remove_at(0);self.nodes(linked,[])
        linked.prepend("B");self.nodes(linked,["B"])

    def test_13_insertion_preserves_existing_node_objects(self):
        linked=SinglyLinkedList([10,20]);before=self.nodes(linked,[10,20])
        linked.insert_at(1,15);after=self.nodes(linked,[10,15,20])
        self.assertIs(after[0],before[0]);self.assertIs(after[2],before[1])
        linked.prepend(5);last=self.nodes(linked,[5,10,15,20])
        self.assertIs(last[1],before[0]);self.assertIs(last[-1],before[-1])

    def test_14_deletion_rewires_without_rebuilding_survivors(self):
        linked=SinglyLinkedList([10,20,30]);before=self.nodes(linked,[10,20,30])
        self.assertEqual(linked.remove_at(1),20)
        after=self.nodes(linked,[10,30]);self.assertIs(after[0],before[0]);self.assertIs(after[1],before[2])
        self.assertTrue(linked.remove(30));self.nodes(linked,[10])

    def test_15_no_flat_backing_collection(self):
        linked=SinglyLinkedList([1,2,3])
        forbidden=[name for name,value in vars(linked).items() if isinstance(value,(list,tuple,dict,set,deque))]
        self.assertEqual(forbidden,[],"Store values in nodes. A temporary list in to_list() is allowed, but a persistent list/dictionary/deque field is not.")
        self.nodes(linked,[1,2,3])

    def test_16_tail_next_stays_none_after_changes(self):
        linked=SinglyLinkedList([1,2]);linked.append(3);linked.remove_at(2);linked.append(4)
        nodes=self.nodes(linked,[1,2,4]);self.assertIsNone(nodes[-1].next)


class LinkedListWebsiteGoalTests(WorkspaceCase):
    def test_17_real_web_workflow_reloads_as_nodes(self):
        self.workspace.workflow_state=[];self.workspace.save(update_fields=["workflow_state"])
        for value in ["A","B","C"]:self.workflow("append",value=value)
        state=self.client.get("/api/state/").json()["workflow"]
        self.assertEqual(state["values"],["A","B","C"])
        self.assertEqual(state["representation"]["mode"],"nodes","The web feature must reconstruct actual linked nodes from saved data.")
        self.assertEqual([x["next"] for x in state["representation"]["rows"]],["N1","N2","None"])
        self.workflow("remove_at",index=0)
        self.assertEqual(self.client.get("/api/state/").json()["workflow"]["values"],["B","C"])
