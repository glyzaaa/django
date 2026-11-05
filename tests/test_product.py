from datetime import timedelta
from urllib.parse import urlparse
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone
from database.models import Comment, Event, Invitation, Membership, Ticket, Workspace
from backend.workspace.services import create_workspace
from .helpers import WorkspaceCase

User = get_user_model()


class ProductTests(WorkspaceCase):
    def member(self, role, name=None):
        name = name or role
        user = User.objects.create_user(username=name, email=f"{name}@example.test", password="Another-example-2026", first_name=name.title())
        membership = Membership.objects.create(workspace=self.workspace, user=user, role=role)
        client = Client(); client.force_login(user)
        return user, membership, client

    def test_anonymous_cannot_read_or_mutate_workspace(self):
        client=Client()
        for path in ["/", "/requests/", "/queue/", "/workflow/", "/reports/", "/api/state/", "/accounts/team/", "/requests/export/"]:
            self.assertEqual(client.get(path).status_code,302,path)
        self.assertEqual(client.post("/items/new/",{}).status_code,302)
        self.assertEqual(Workspace.objects.count(),1)

    def test_product_pages_render_without_placeholder_actions(self):
        for path in ["/", "/requests/", "/requests/?view=board", "/reports/", "/accounts/team/", "/accounts/profile/", "/accounts/workspaces/new/", "/accounts/password/change/"]:
            response=self.client.get(path)
            self.assertEqual(response.status_code,200,path)
            self.assertNotContains(response,'href="#"')
        self.assertEqual(self.client.get("/accounts/logout/").status_code,405)

    def test_registration_creates_real_user_and_owned_workspace(self):
        client=Client()
        response=client.post("/accounts/register/",{"username":"fresh","first_name":"Sam","email":"sam@example.test","workspace_name":"Sam's team","password1":"Strong-example-2026","password2":"Strong-example-2026","sample_data":"on"})
        self.assertEqual(response.status_code,302)
        user=User.objects.get(username="fresh")
        self.assertTrue(user.check_password("Strong-example-2026"))
        member=Membership.objects.get(user=user)
        self.assertEqual(member.role,"owner")
        self.assertEqual(member.workspace.tickets.count(),6)
        self.assertEqual(client.get("/").status_code,200)

    def test_registration_does_not_redirect_to_untrusted_site(self):
        client=Client()
        response=client.post("/accounts/register/?next=https://untrusted.example/",{"username":"fresh","first_name":"Sam","email":"sam@example.test","workspace_name":"New","password1":"Strong-example-2026","password2":"Strong-example-2026"})
        self.assertEqual(response.url,"/")

    def test_email_uniqueness_is_case_insensitive_in_database(self):
        with self.assertRaises(IntegrityError),transaction.atomic():
            User.objects.create_user(username="duplicate",email="TEACHER@EXAMPLE.TEST")

    def test_login_logout_and_persistent_workspace(self):
        self.client.post("/accounts/logout/")
        self.assertEqual(self.client.get("/").status_code,302)
        response=self.client.post("/accounts/login/",{"username":"teacher","password":"Desk-example-2026"})
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.client.get("/api/state/").json()["workspace"]["id"],str(self.workspace.id))

    def test_failed_login_is_throttled(self):
        client=Client()
        for _ in range(5):
            self.assertContains(client.post("/accounts/login/",{"username":"teacher","password":"wrong"}),"correct username and password")
        self.assertContains(client.post("/accounts/login/",{"username":"teacher","password":"Desk-example-2026"}),"Too many sign-in attempts")
        self.assertNotIn("_auth_user_id",client.session)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_uses_real_django_token_and_mail(self):
        client=Client()
        response=client.post("/accounts/password/reset/",{"email":self.user.email})
        self.assertEqual(response.status_code,302)
        self.assertEqual(len(mail.outbox),1)
        url=next(line for line in mail.outbox[0].body.splitlines() if "http://" in line)
        response=client.get(urlparse(url).path,follow=True)
        self.assertEqual(response.status_code,200)
        response=client.post(response.request["PATH_INFO"],{"new_password1":"New-secure-example-2026","new_password2":"New-secure-example-2026"})
        self.assertEqual(response.status_code,302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-secure-example-2026"))

    def test_viewer_has_read_access_but_all_mutations_are_forbidden(self):
        _,_,client=self.member("viewer")
        item=self.item()
        for path in ["/", "/requests/", f"/items/{item.id}/", "/queue/", "/workflow/", "/reports/", "/api/state/", "/requests/export/"]:
            self.assertEqual(client.get(path).status_code,200,path)
        for path,data in [("/items/new/",{}),(f"/items/{item.id}/move/",{"status":"done"}),
                          (f"/items/{item.id}/archive/",{}),(f"/queue/join/{item.id}/",{}),
                          ("/queue/serve/",{}),("/workflow/",{"operation":"append","value":"Bad"}),
                          (f"/items/{item.id}/",{"body":"Bad"}),("/settings/",{"name":"Bad","accent":"teal"}),
                          ("/accounts/team/",{"email":"bad@example.test","role":"agent"})]:
            self.assertEqual(client.post(path,data).status_code,403,path)

    def test_agent_can_edit_requests_but_not_manage_settings_or_team(self):
        _,_,client=self.member("agent")
        item=self.item()
        self.assertEqual(client.post(f"/items/{item.id}/move/",{"status":"doing"}).status_code,302)
        self.assertEqual(client.get("/settings/").status_code,403)
        self.assertEqual(client.post("/accounts/team/",{"email":"x@example.test","role":"agent"}).status_code,403)

    def test_manager_can_change_settings_but_not_membership(self):
        _,_,client=self.member("manager")
        self.assertEqual(client.post("/settings/",{"name":"Managed","accent":"forest"}).status_code,302)
        self.assertEqual(client.post("/accounts/team/",{"email":"x@example.test","role":"owner"}).status_code,403)

    def test_removed_membership_revokes_existing_session_access(self):
        _,membership,client=self.member("agent")
        self.assertEqual(client.get("/").status_code,200)
        membership.delete()
        self.assertEqual(client.get("/api/state/").status_code,302)
        self.assertEqual(client.post("/queue/serve/").status_code,302)

    def test_tampered_workspace_session_cannot_grant_access(self):
        other=Workspace.objects.create(name="Secret")
        session=self.client.session;session["workspace_id"]=str(other.id);session.save()
        self.assertEqual(self.client.get("/api/state/").json()["workspace"]["id"],str(self.workspace.id))
        self.assertEqual(self.client.post(reverse("accounts:switch_workspace",args=[other.id])).status_code,404)

    def test_switch_between_two_authorized_workspaces(self):
        other=create_workspace(owner=self.user,name="Second team",seed=False)
        self.assertEqual(self.client.post(reverse("accounts:switch_workspace",args=[other.id])).status_code,302)
        self.assertEqual(self.client.get("/api/state/").json()["workspace"]["name"],"Second team")
        self.assertEqual(self.client.get("/api/state/").json()["items"],[])

    def test_invitation_acceptance_is_email_bound_and_one_time(self):
        self.client.post("/accounts/team/",{"email":"new@example.test","role":"agent"})
        invitation=Invitation.objects.get(email="new@example.test")
        client=Client();user=User.objects.create_user(username="new",email="new@example.test")
        client.force_login(user)
        path=reverse("accounts:accept_invite",args=[invitation.id])
        self.assertEqual(client.get(path).status_code,200)
        self.assertEqual(client.post(path).status_code,302)
        self.assertEqual(Membership.objects.get(user=user,workspace=self.workspace).role,"agent")
        self.assertEqual(client.post(path).status_code,403)

    def test_invitation_rejects_wrong_account_and_expiry(self):
        invitation=Invitation.objects.create(workspace=self.workspace,email="someone@example.test",role="agent",expires_at=timezone.now()+timedelta(days=1))
        path=reverse("accounts:accept_invite",args=[invitation.id])
        self.assertEqual(self.client.post(path).status_code,403)
        invitation.email=self.user.email;invitation.expires_at=timezone.now()-timedelta(seconds=1);invitation.save()
        self.assertEqual(self.client.post(path).status_code,403)

    def test_revoke_invitation_and_prevent_owner_role_injection(self):
        self.assertEqual(self.client.post("/accounts/team/",{"email":"someone@example.test","role":"owner"}).status_code,422)
        self.client.post("/accounts/team/",{"email":"someone@example.test","role":"viewer"})
        invitation=Invitation.objects.get(email="someone@example.test")
        self.client.post(reverse("accounts:revoke_invite",args=[invitation.id]))
        invitation.refresh_from_db();self.assertFalse(invitation.pending)

    def test_removing_member_clears_assignments_and_preserves_notes(self):
        user,member,_=self.member("agent")
        item=self.item();item.assignee=user;item.save()
        Comment.objects.create(ticket=item,author=user,body="Keep this handoff")
        self.assertEqual(self.client.post(reverse("accounts:remove_member",args=[member.id])).status_code,302)
        item.refresh_from_db();self.assertIsNone(item.assignee)
        self.assertEqual(item.comments.count(),1)
        owner=Membership.objects.get(user=self.user,workspace=self.workspace)
        self.assertEqual(self.client.post(reverse("accounts:remove_member",args=[owner.id])).status_code,403)

    def test_assignment_is_restricted_to_workspace_agents(self):
        stranger=User.objects.create_user(username="stranger",email="stranger@example.test")
        data={"title":"Assigned","category":"Support","status":"todo","priority":"medium","assignee":stranger.pk}
        self.assertEqual(self.client.post("/items/new/",data).status_code,422)
        agent,_,_=self.member("agent")
        data["assignee"]=agent.id
        self.assertEqual(self.client.post("/items/new/",data).status_code,302)
        self.assertEqual(Ticket.objects.get(title="Assigned").assignee,agent)

    def test_stale_edit_cannot_overwrite_a_teammate(self):
        item=self.item();version=item.version
        data={"title":"First update","description":"","category":"Support","status":"todo","priority":"medium","version":version}
        self.assertEqual(self.client.post(reverse("workspace:edit",args=[item.id]),data).status_code,302)
        data["title"]="Stale overwrite"
        response=self.client.post(reverse("workspace:edit",args=[item.id]),data)
        self.assertContains(response,"Someone updated",status_code=422)
        item.refresh_from_db();self.assertEqual(item.title,"First update")

    def test_notes_are_owned_escaped_and_retained_after_restore(self):
        item=self.item()
        self.client.post(reverse("workspace:detail",args=[item.id]),{"body":"<script>bad()</script>"})
        note=Comment.objects.get(ticket=item);self.assertEqual(note.author,self.user)
        response=self.client.get(reverse("workspace:detail",args=[item.id]))
        self.assertContains(response,"&lt;script&gt;")
        self.assertNotContains(response,"<script>bad()")
        self.client.post(reverse("workspace:archive_item",args=[item.id]))
        self.client.post(reverse("workspace:restore_item",args=[item.id]))
        self.assertEqual(item.comments.count(),1)

    def test_foreign_request_detail_note_and_withdraw_are_blocked(self):
        outsider=User.objects.create_user(username="outsider",email="outsider@example.test")
        private=create_workspace(owner=outsider,seed=False)
        item=Ticket.objects.create(workspace=private,title="Private")
        for path in [f"/items/{item.id}/",f"/queue/withdraw/{item.id}/"]:
            response=self.client.get(path) if path.endswith(f"{item.id}/") and path.startswith("/items/") else self.client.post(path)
            self.assertEqual(response.status_code,404)
        self.assertEqual(self.client.post(f"/items/{item.id}/",{"body":"Bad"}).status_code,404)

    def test_queue_start_assigns_actual_selected_request_and_records_actor(self):
        a=self.item("First");b=self.item("Second");self.join(a);self.join(b)
        selected=self.client.get("/api/state/").json()["queue"]["selected_next"]
        self.client.post("/queue/serve/")
        item=Ticket.objects.get(pk=selected)
        self.assertEqual(item.assignee,self.user);self.assertIsNotNone(item.started_at)
        self.assertEqual(Event.objects.filter(kind="served").latest("id").actor,self.user)

    def test_withdraw_preserves_other_arrivals_and_ticket(self):
        a,b,c=self.item("A"),self.item("B"),self.item("C")
        for item in [a,b,c]:self.join(item)
        self.client.post(reverse("workspace:queue_withdraw",args=[b.id]))
        self.assertEqual(self.fresh().queue_state,[a.id,c.id])
        b.refresh_from_db();self.assertEqual(b.status,"todo");self.assertIsNone(b.queued_at)

    def test_reports_reflect_database_and_csv_prevents_formula_execution(self):
        item=self.item("=HYPERLINK(\"bad\")",priority="high")
        response=self.client.get("/reports/")
        self.assertEqual(response.context["report_total"],7)
        csv=self.client.get("/requests/export/?q=HYPERLINK")
        self.assertIn(b"'=HYPERLINK",csv.content)
        self.assertNotIn(b"reading-room",csv.content)
        self.assertEqual(csv["Content-Type"],"text/csv; charset=utf-8")

    def test_request_list_is_paginated_and_filters_combine(self):
        Ticket.objects.bulk_create([Ticket(workspace=self.workspace,title=f"Test {i}",priority="high") for i in range(31)])
        response=self.client.get("/requests/?priority=high&status=todo&page=2")
        self.assertLessEqual(len(response.context["items"]),25)
        self.assertEqual(response.context["items"].paginator.count,32)
        self.assertTrue(all(x.priority=="high" and x.status=="todo" for x in response.context["items"]))

    def test_stale_queue_submission_does_not_start_a_second_request(self):
        a,b=self.item("A"),self.item("B")
        self.join(a);self.join(b)
        selected=self.client.get("/api/state/").json()["queue"]["selected_next"]
        payload={"expected_next":selected}
        self.client.post("/queue/serve/",payload)
        response=self.client.post("/queue/serve/",payload,follow=True)
        self.assertContains(response,"queue changed")
        self.assertEqual(len(self.fresh().queue_state),1)
        self.assertEqual(Event.objects.filter(kind="served").count(),1)

    def test_owner_can_change_role_and_revocation_applies_on_next_request(self):
        user,member,client=self.member("agent")
        item=self.item();item.assignee=user;item.save()
        self.assertEqual(client.post(f"/items/{item.id}/move/",{"status":"doing"}).status_code,302)
        self.assertEqual(self.client.post(reverse("accounts:update_role",args=[member.id]),{"role":"viewer"}).status_code,302)
        item.refresh_from_db();self.assertIsNone(item.assignee)
        self.assertEqual(client.post(f"/items/{item.id}/move/",{"status":"done"}).status_code,403)
        self.client.post(reverse("accounts:update_role",args=[member.id]),{"role":"agent"})
        self.assertEqual(client.post(f"/items/{item.id}/move/",{"status":"done"}).status_code,302)

    def test_role_management_cannot_escalate_to_owner_or_cross_workspace(self):
        _,member,client=self.member("agent")
        path=reverse("accounts:update_role",args=[member.id])
        self.assertEqual(client.post(path,{"role":"manager"}).status_code,403)
        self.assertEqual(self.client.post(path,{"role":"owner"}).status_code,400)
        owner=Membership.objects.get(user=self.user,workspace=self.workspace)
        self.assertEqual(self.client.post(reverse("accounts:update_role",args=[owner.id]),{"role":"viewer"}).status_code,403)
        outsider=User.objects.create_user(username="outsider",email="outsider@example.test")
        private=create_workspace(owner=outsider,seed=False)
        foreign=Membership.objects.get(user=outsider,workspace=private)
        self.assertEqual(self.client.post(reverse("accounts:update_role",args=[foreign.id]),{"role":"viewer"}).status_code,404)

    def test_health_reports_database_failure_even_with_a_session_cookie(self):
        from unittest.mock import patch
        from django.db import DatabaseError
        with patch("django.db.connection.cursor", side_effect=DatabaseError("offline")):
            response=self.client.get("/health/")
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json(),{"status":"unavailable"})
