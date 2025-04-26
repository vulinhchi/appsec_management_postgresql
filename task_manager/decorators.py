from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def require_groups(groups):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if not request.user.groups.filter(name__in=groups).exists():
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
