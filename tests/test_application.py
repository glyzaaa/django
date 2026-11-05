from unittest.mock import patch
from django.contrib.staticfiles import finders
from django.test import Client, override_settings
from django.urls import reverse
from backend.dsa.queue import ServiceQueue
from backend.dsa.singly_linked_list import SinglyLinkedList
from database.models import Event, Ticket, Workspace
from .helpers import WorkspaceCase
from django.contrib.auth import get_user_model
from backend.workspace.services import create_workspace


class ApplicationTests(WorkspaceCase):
    def test_every_page_and_view_renders(self):
        for path in ["/", "/requests/?view=list", "/requests/?status=todo", "/requests/?q=reading", "/items/new/", "/queue/",
                     "/workflow/", "/archive/", "/activity/", "/settings/", "/guide/", "/api/state/", "/health/"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_seeding_is_once_per_workspace(self):
        for path in ["/", "/workflow/", "/queue/", "/"]:
            self.client.get(path)
        self.assertEqual(self.workspace.tickets.count(), 6)
        self.assertEqual(Workspace.objects.count(), 1)

    def test_create_edit_move_and_search(self):
        item = self.item("Preserve this", priority="high")
        response = self.client.post(reverse("workspace:edit", args=[item.id]), {
            "title": "Updated title", "description": "New details", "category": "Support",
            "status": "todo", "priority": "low", "due_date": "2027-01-20", "version": item.version})
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.title, "Updated title")
        self.assertEqual(str(item.due_date), "2027-01-20")
        self.assertContains(self.client.get("/requests/?q=Updated%20title&view=list"), "Updated title")
        self.assertEqual(self.client.post(reverse("workspace:move", args=[item.id]), {"status": "done"}).status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, "done")

    def test_invalid_forms_do_not_create_items(self):
        before = self.workspace.tickets.count()
        empty = self.client.post(reverse("workspace:new"), {})
        self.assertEqual(empty.status_code, 422)
        self.assertTrue(empty.context["form"].errors)
        for changes in [{"title": " "}, {"title": "x"*101}, {"category": " "}, {"description": "x"*1501},
                        {"status": "invented"}, {"priority": "urgent"}, {"due_date": "2026-02-31"}]:
            data = {"title": "Valid", "description": "", "category": "General", "status": "todo", "priority": "medium", "due_date": ""}
            data.update(changes)
            with self.subTest(changes=changes.keys()):
                self.assertEqual(self.client.post(reverse("workspace:new"), data).status_code, 422)
        self.assertEqual(self.workspace.tickets.count(), before)

    def test_bad_move_and_get_mutations_are_rejected(self):
        item = self.item()
        self.assertEqual(self.client.post(reverse("workspace:move", args=[item.id]), {"status": "bad"}).status_code, 400)
        for name, args in [("move", [item.id]), ("archive_item", [item.id]), ("restore_item", [item.id]),
                           ("queue_join", [item.id]), ("queue_serve", [])]:
            self.assertEqual(self.client.get(reverse("workspace:"+name, args=args)).status_code, 405)

    def test_archive_restore_preserves_details_and_does_not_requeue(self):
        item = self.item("Remember details", priority="high", due_date="2027-01-01")
        self.join(item)
        self.client.post(reverse("workspace:archive_item", args=[item.id]))
        self.assertEqual(self.fresh().queue_state, [])
        self.assertContains(self.client.get("/archive/"), "Remember details")
        self.client.post(reverse("workspace:restore_item", args=[item.id]))
        item.refresh_from_db()
        self.assertFalse(item.archived)
        self.assertEqual((item.title, item.description, item.priority, item.status, str(item.due_date)),
                         ("Remember details", "Details to preserve", "high", "todo", "2027-01-01"))
        self.assertEqual(self.fresh().queue_state, [])

    def test_queue_persists_arrival_order_and_rejects_duplicates(self):
        a, b = self.item("First"), self.item("Second")
        for item in [a,b,a]:
            self.join(item)
        self.assertEqual(self.fresh().queue_state, [a.id,b.id])
        self.assertEqual(self.client.get("/api/state/").json()["queue"]["arrival_order"], [a.id,b.id])

    def test_queue_can_only_take_todo_items(self):
        item = self.item(status="done")
        self.join(item)
        self.assertEqual(self.fresh().queue_state, [])

    def test_serve_calls_real_class_and_keeps_fields(self):
        a,b = self.item("A"),self.item("B", priority="high")
        self.join(a);self.join(b)
        expected = ServiceQueue([a.id,b.id]).peek()
        original = ServiceQueue.dequeue
        calls = []
        def traced(instance):
            calls.append(True)
            return original(instance)
        with patch.object(ServiceQueue, "dequeue", traced):
            self.client.post(reverse("workspace:queue_serve"))
        self.assertEqual(len(calls), 1)
        selected = Ticket.objects.get(pk=expected)
        self.assertEqual(selected.status, "doing")
        self.assertEqual(selected.description, "Details to preserve")
        self.assertNotIn(expected, self.fresh().queue_state)
        self.assertEqual(self.workspace.events.filter(kind="served").latest("id").details["item_id"], expected)

    def test_empty_service_is_safe(self):
        response = self.client.post(reverse("workspace:queue_serve"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "service queue is empty")
        self.assertEqual(self.fresh().queue_state, [])

    def test_bad_student_dequeue_rolls_back_all_state(self):
        a = self.item("A")
        self.join(a)
        with patch.object(ServiceQueue, "dequeue", lambda self: 987654321):
            self.client.post(reverse("workspace:queue_serve"))
        a.refresh_from_db()
        self.assertEqual(a.status, "todo")
        self.assertEqual(self.fresh().queue_state, [a.id])
        self.assertFalse(self.workspace.events.filter(kind="served").exists())

    def test_moving_out_of_todo_withdraws_waiting_item(self):
        a = self.item("A")
        self.join(a)
        self.client.post(reverse("workspace:move", args=[a.id]), {"status":"doing"})
        self.assertEqual(self.fresh().queue_state, [])

    def test_workflow_operations_save_and_reload(self):
        self.workspace.workflow_state = []
        self.workspace.save(update_fields=["workflow_state"])
        sequence = [
            ("append", {"value":"Review"}, ["Review"]),
            ("prepend", {"value":"Receive"}, ["Receive","Review"]),
            ("insert_at", {"index":1,"value":"Validate"}, ["Receive","Validate","Review"]),
            ("get", {"index":1}, ["Receive","Validate","Review"]),
            ("index_of", {"value":"Review"}, ["Receive","Validate","Review"]),
            ("remove_at", {"index":0}, ["Validate","Review"]),
            ("remove", {"value":"Validate"}, ["Review"]),
        ]
        for op, values, expected in sequence:
            with self.subTest(op=op):
                self.assertEqual(self.workflow(op, **values).status_code, 302)
                self.assertEqual(self.fresh().workflow_state, expected)
                self.assertEqual(self.client.get("/api/state/").json()["workflow"]["values"], expected)

    def test_workflow_calls_student_method(self):
        original = SinglyLinkedList.insert_at
        calls=[]
        def traced(instance,index,value):
            calls.append((index,value))
            return original(instance,index,value)
        with patch.object(SinglyLinkedList,"insert_at",traced):
            self.workflow("insert_at", index=1, value="Verify")
        self.assertEqual(calls,[(1,"Verify")])
        self.assertEqual(self.fresh().workflow_state[1],"Verify")

    def test_invalid_workflow_requests_preserve_saved_values(self):
        before=list(self.workspace.workflow_state)
        for values in [{"operation":"get","index":-1}, {"operation":"remove_at","index":999},
                       {"operation":"insert_at","index":"abc","value":"A"},
                       {"operation":"append","value":" "}, {"operation":"append","value":"x"*81},
                       {"operation":"not_a_method","value":"A"}]:
            with self.subTest(values=values):
                self.assertEqual(self.client.post("/workflow/",values).status_code,422)
                self.assertEqual(self.fresh().workflow_state,before)

    def test_mutating_get_rolls_back(self):
        before=list(self.workspace.workflow_state)
        def broken(instance,index):
            instance.append("Bad mutation")
            return "Bad"
        with patch.object(SinglyLinkedList,"get",broken):
            self.assertEqual(self.workflow("get",index=0).status_code,422)
        self.assertEqual(self.fresh().workflow_state,before)

    def test_preferences_do_not_overwrite_structures(self):
        a=self.item("A");self.join(a)
        before=list(self.fresh().workflow_state)
        self.assertEqual(self.client.post("/settings/",{"name":"Team Cedar","accent":"violet"}).status_code,302)
        self.assertEqual(self.fresh().name,"Team Cedar")
        self.assertEqual(self.workspace.queue_state,[a.id])
        self.assertEqual(self.workspace.workflow_state,before)
        self.assertEqual(self.client.post("/settings/",{"name":" ","accent":"invalid"}).status_code,422)

    def test_browser_workspaces_are_isolated_on_every_object_route(self):
        a=self.item("Keep private")
        other=Client()
        other_user=get_user_model().objects.create_user(username="other",email="other@example.test")
        create_workspace(owner=other_user)
        other.force_login(other_user)
        other.get("/")
        self.assertNotEqual(other.session["workspace_id"],str(self.workspace.id))
        self.assertNotContains(other.get("/"),"Keep private")
        for name in ["edit","archive_item","queue_join","restore_item"]:
            path=reverse("workspace:"+name,args=[a.id])
            response=other.get(path) if name=="edit" else other.post(path)
            self.assertEqual(response.status_code,404)
        other_ids=[x["id"] for x in other.get("/api/state/").json()["items"]]
        self.assertNotIn(a.id,other_ids)

    def test_same_browser_cookie_reopens_persisted_workspace(self):
        a=self.item("Persistent request");self.join(a)
        other=Client();other.cookies=self.client.cookies.copy()
        self.assertEqual(other.get("/api/state/").json()["queue"]["arrival_order"],[a.id])
        self.assertEqual(Workspace.objects.count(),1)

    def test_user_text_is_escaped_in_pages(self):
        value='<script>alert("x")</script>'
        self.item(value)
        response=self.client.get("/")
        self.assertNotContains(response,value)
        self.assertContains(response,"&lt;script&gt;")
        self.workflow("append",value=value)
        self.assertNotContains(self.client.get("/workflow/"),value)

    def test_csrf_is_required_with_real_browser_checks(self):
        client=Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        client.get("/items/new/")
        values={"title":"No token","category":"General","status":"todo","priority":"medium"}
        self.assertEqual(client.post("/items/new/",values).status_code,403)
        token=client.cookies["csrftoken"].value
        self.assertEqual(client.post("/items/new/",{**values,"csrfmiddlewaretoken":token}).status_code,302)

    def test_assets_exist_and_sources_are_not_public(self):
        for asset in ["app.css","app.js","favicon.svg"]:
            self.assertTrue(finders.find(asset),asset)
        for path in ["/backend/dsa/queue.py","/database/models.py","/database/data/flowdesk.sqlite3","/static/../backend/dsa/queue.py"]:
            self.assertEqual(self.client.get(path).status_code,404)

    @override_settings(DEBUG=False)
    def test_friendly_production_404(self):
        self.assertContains(self.client.get("/missing-page/"),"not available",status_code=404)

    def test_activity_pagination_is_bounded(self):
        Event.objects.bulk_create([Event(workspace=self.workspace,kind="test",summary=f"Entry {i}") for i in range(31)])
        response=self.client.get("/activity/?page=2")
        self.assertEqual(response.status_code,200)
        self.assertLessEqual(len(response.context["events"]),25)
