from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def workspace_access(edit=False, manage=False):
    def decorate(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.workspace is None:
                return redirect("accounts:new_workspace")
            if (edit and not request.membership.can_edit) or (manage and not request.membership.can_manage):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorate
