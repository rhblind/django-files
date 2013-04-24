# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured


class NextMixin(object):
    """
    A mixin which returns the first valid value from
    either "next" from POST data or success_url. If neither
    is available, try to get the absolute url from model.
    """
    def get_success_url(self):
        url = self.request.POST.get("next", None) or self.success_url
        if not url:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured("No URL to redirect to. Provide a next value, success_url"
                                           " or a get_absolute_url method on the Model.")
        return url


class AttachmentFormSetMixin(object):
    """
    Render a formset instead of a form
    """
    pass
