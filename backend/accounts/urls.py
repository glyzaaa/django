from django.contrib.auth import views as auth
from django.urls import path, reverse_lazy
from . import views
app_name = "accounts"
urlpatterns = [
    path("login/", views.DeskLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("password/change/", auth.PasswordChangeView.as_view(template_name="accounts/password_form.html", success_url=reverse_lazy("accounts:password_change_done")), name="password_change"),
    path("password/changed/", auth.PasswordChangeDoneView.as_view(template_name="accounts/password_changed.html"), name="password_change_done"),
    path("password/reset/", auth.PasswordResetView.as_view(template_name="accounts/password_reset.html", email_template_name="accounts/reset_email.txt", subject_template_name="accounts/reset_subject.txt", success_url=reverse_lazy("accounts:password_reset_done")), name="password_reset"),
    path("password/reset/sent/", auth.PasswordResetDoneView.as_view(template_name="accounts/password_sent.html"), name="password_reset_done"),
    path("password/reset/<uidb64>/<token>/", auth.PasswordResetConfirmView.as_view(template_name="accounts/password_confirm.html", success_url=reverse_lazy("accounts:password_reset_complete")), name="password_reset_confirm"),
    path("password/reset/complete/", auth.PasswordResetCompleteView.as_view(template_name="accounts/password_complete.html"), name="password_reset_complete"),
    path("workspaces/new/", views.new_workspace, name="new_workspace"),
    path("workspaces/<uuid:workspace_id>/switch/", views.switch_workspace, name="switch_workspace"),
    path("team/", views.team, name="team"),
    path("team/<int:member_id>/role/", views.update_role, name="update_role"),
    path("team/<int:member_id>/remove/", views.remove_member, name="remove_member"),
    path("invites/<uuid:invite_id>/revoke/", views.revoke_invite, name="revoke_invite"),
    path("invites/<uuid:invite_id>/", views.accept_invite, name="accept_invite"),
]
