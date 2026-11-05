from django.core.exceptions import ValidationError
from database.models import Membership

class WorkspaceMiddleware:
    """Recheck membership every request. A session ID never grants access."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        request.workspace = request.membership = None
        if not request.path.startswith(("/static/", "/admin/", "/health/")) and request.user.is_authenticated:
            memberships = Membership.objects.select_related("workspace").filter(user=request.user)
            selected = None
            try:
                key = request.session.get("workspace_id")
                if key:
                    selected = memberships.filter(workspace_id=key).first()
            except (ValidationError, ValueError, TypeError):
                pass
            selected = selected or memberships.order_by("joined_at").first()
            if selected:
                request.membership, request.workspace = selected, selected.workspace
                if request.session.get("workspace_id") != str(selected.workspace_id):
                    request.session["workspace_id"] = str(selected.workspace_id)
        return self.get_response(request)
