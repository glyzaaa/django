from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST
from database.models import Invitation, Membership, Workspace
from backend.workspace import services
from .forms import DeskAuthenticationForm, InviteForm, ProfileForm, RegistrationForm, WorkspaceForm

class DeskLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = DeskAuthenticationForm
    redirect_authenticated_user = True

@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("workspace:dashboard")
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
                workspace = services.create_workspace(owner=user, name=form.cleaned_data["workspace_name"], seed=form.cleaned_data["sample_data"])
        except IntegrityError:
            form.add_error(None, "That username or email has just been registered. Choose another or sign in.")
            return render(request, "accounts/register.html", {"form": form}, status=422)
        login(request, user)
        request.session["workspace_id"] = str(workspace.id)
        destination = request.GET.get("next", "")
        if not url_has_allowed_host_and_scheme(destination, {request.get_host()}, require_https=request.is_secure()):
            destination = reverse("workspace:dashboard")
        return redirect(destination)
    return render(request, "accounts/register.html", {"form": form}, status=422 if request.method == "POST" else 200)

@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    form = ProfileForm(request.POST if request.method == "POST" else None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form, "page": "profile"}, status=422 if request.method == "POST" else 200)

@login_required
@require_http_methods(["GET", "POST"])
def new_workspace(request):
    form = WorkspaceForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        workspace = services.create_workspace(owner=request.user, name=form.cleaned_data["name"], seed=form.cleaned_data["sample_data"])
        request.session["workspace_id"] = str(workspace.id)
        return redirect("workspace:dashboard")
    return render(request, "accounts/new_workspace.html", {"form": form, "page": "team"}, status=422 if request.method == "POST" else 200)

@login_required
@require_POST
def switch_workspace(request, workspace_id):
    membership = get_object_or_404(Membership, workspace_id=workspace_id, user=request.user)
    request.session["workspace_id"] = str(membership.workspace_id)
    return redirect("workspace:dashboard")

@login_required
@require_http_methods(["GET", "POST"])
def team(request):
    if request.workspace is None:
        return redirect("accounts:new_workspace")
    form = InviteForm(request.POST if request.method == "POST" else None)
    invitation_url = ""
    if request.method == "POST":
        if request.membership.role != "owner":
            raise PermissionDenied
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            if request.workspace.memberships.filter(user__email__iexact=email).exists():
                form.add_error("email", "This person already belongs to the team.")
            else:
                with transaction.atomic():
                    locked = Workspace.objects.select_for_update().get(pk=request.workspace.pk)
                    locked.invitations.filter(email__iexact=email, accepted_at__isnull=True).update(revoked=True)
                    invite = Invitation.objects.create(workspace=locked, email=email, role=form.cleaned_data["role"], created_by=request.user, expires_at=timezone.now()+timedelta(days=7))
                    services.log(locked, "team", f"Invited {email} as {invite.role}.", actor=request.user)
                invitation_url = request.build_absolute_uri(reverse("accounts:accept_invite", args=[invite.id]))
                messages.success(request, "Invitation created. Share this private link; it expires in seven days.")
                form = InviteForm()
    members = request.workspace.memberships.select_related("user").order_by("joined_at")
    invitations = request.workspace.invitations.filter(accepted_at__isnull=True, revoked=False, expires_at__gt=timezone.now()).order_by("-created_at") if request.membership.role == "owner" else []
    return render(request, "accounts/team.html", {"page": "team", "form": form, "members": members, "invitations": invitations, "invitation_url": invitation_url}, status=422 if request.method == "POST" and form.errors else 200)

@login_required
@require_POST
def remove_member(request, member_id):
    if not request.membership or request.membership.role != "owner":
        raise PermissionDenied
    with transaction.atomic():
        Workspace.objects.select_for_update().get(pk=request.workspace.pk)
        member = get_object_or_404(Membership, pk=member_id, workspace=request.workspace)
        if member.role == "owner":
            raise PermissionDenied("The owner cannot be removed.")
        request.workspace.tickets.filter(assignee=member.user).update(assignee=None, version=F("version")+1, updated_at=timezone.now())
        services.log(request.workspace, "team", f"Removed {member.user.get_username()} from the team.", actor=request.user)
        member.delete()
    messages.success(request, "Member removed. Their assignments are now unassigned.")
    return redirect("accounts:team")

@login_required
@require_POST
def revoke_invite(request, invite_id):
    if not request.membership or request.membership.role != "owner":
        raise PermissionDenied
    invitation = get_object_or_404(Invitation, pk=invite_id, workspace=request.workspace)
    invitation.revoked = True
    invitation.save(update_fields=["revoked"])
    messages.success(request, "Invitation revoked.")
    return redirect("accounts:team")

@login_required
@require_http_methods(["GET", "POST"])
def accept_invite(request, invite_id):
    invitation = get_object_or_404(Invitation.objects.select_related("workspace"), pk=invite_id)
    if request.method == "POST":
        with transaction.atomic():
            Workspace.objects.select_for_update().get(pk=invitation.workspace_id)
            invitation = Invitation.objects.select_for_update().get(pk=invite_id)
            if not invitation.pending or request.user.email.casefold() != invitation.email.casefold():
                raise PermissionDenied("This invitation is expired, used, or belongs to another email address.")
            Membership.objects.get_or_create(workspace=invitation.workspace, user=request.user, defaults={"role": invitation.role})
            invitation.accepted_at = timezone.now()
            invitation.save(update_fields=["accepted_at"])
            services.log(invitation.workspace, "team", f"{request.user.get_username()} joined the team.", actor=request.user)
        request.session["workspace_id"] = str(invitation.workspace_id)
        return redirect("workspace:dashboard")
    return render(request, "accounts/invitation.html", {"invitation": invitation, "email_matches": request.user.email.casefold() == invitation.email.casefold()})


@login_required
@require_POST
def update_role(request, member_id):
    from .forms import MemberRoleForm
    if not request.membership or request.membership.role != "owner":
        raise PermissionDenied
    form = MemberRoleForm(request.POST)
    if not form.is_valid():
        return render(request, "error.html", {"code": 400, "message": "Choose an agent, manager, or viewer role."}, status=400)
    with transaction.atomic():
        Workspace.objects.select_for_update().get(pk=request.workspace.pk)
        member = get_object_or_404(Membership, pk=member_id, workspace=request.workspace)
        if member.role == "owner":
            raise PermissionDenied("The owner role cannot be changed here.")
        member.role = form.cleaned_data["role"]
        member.save(update_fields=["role"])
        if not member.can_edit:
            request.workspace.tickets.filter(assignee=member.user).update(assignee=None, version=F("version")+1, updated_at=timezone.now())
        services.log(request.workspace, "team", f"Changed {member.user.get_username()} to {member.get_role_display()}.", actor=request.user)
    messages.success(request, "Team role updated.")
    return redirect("accounts:team")
