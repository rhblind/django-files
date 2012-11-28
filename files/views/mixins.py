from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings


class PermissionsRequiredMixin(object):
    """
    View mixin which verifies that the logged in user has the specified
    permissions.

    Settings::

        `required_permissions` - list/tuple of required permissions

    Example Usage::

        class SomeView(PermissionsRequiredMixin, ListView):
            ...
            required_permissions = (
                'app1.permission_a',
                'app2.permission_b',
            )
            ...
    """
    required_permissions = ()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perms(self.required_permissions):
            messages.error(
                request,
                "You do not have the permission required to perform the "
                "requested operation.")
            return redirect(settings.LOGIN_URL)
        return super(PermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)
