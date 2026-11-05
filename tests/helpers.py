from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from backend.workspace.services import create_workspace
from django.urls import reverse
from database.models import Ticket, Workspace


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class WorkspaceCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="teacher", email="teacher@example.test", password="Desk-example-2026", first_name="Alex")
        self.workspace = create_workspace(owner=self.user, name="Campus service desk")
        self.client.force_login(self.user)
        self.client.get(reverse("workspace:board"))

    def item(self, title="Demo item", **changes):
        values = {"title": title, "description": "Details to preserve", "category": "Demo",
                  "status": "todo", "priority": "medium", "due_date": ""}
        values.update(changes)
        response = self.client.post(reverse("workspace:new"), values)
        self.assertEqual(response.status_code, 302, response.content[:500])
        return Ticket.objects.filter(workspace=self.workspace, title=title).latest("id")

    def join(self, item):
        return self.client.post(reverse("workspace:queue_join", args=[item.id]))

    def fresh(self):
        self.workspace.refresh_from_db()
        return self.workspace

    def workflow(self, operation, **values):
        return self.client.post(reverse("workspace:workflow"), {"operation": operation, **values})
