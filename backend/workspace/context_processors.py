from django.db.models import Count, Q
from database.models import STATUSES


def workspace_context(request):
    workspace = getattr(request, "workspace", None)
    if workspace is None:
        return {"statuses": STATUSES}
    counts = workspace.tickets.aggregate(
        active=Count("id", filter=Q(archived=False)),
        todo=Count("id", filter=Q(archived=False, status="todo")),
        doing=Count("id", filter=Q(archived=False, status="doing")),
        done=Count("id", filter=Q(archived=False, status="done")),
        archived=Count("id", filter=Q(archived=True)),
    )
    return {"workspace": workspace, "counts": counts, "statuses": STATUSES,
            "membership": request.membership, "can_edit": request.membership.can_edit, "can_manage": request.membership.can_manage,
            "workspace_memberships": request.user.desk_memberships.select_related("workspace"),
            "waiting_count": len(workspace.queue_state), "workflow_count": len(workspace.workflow_state)}
