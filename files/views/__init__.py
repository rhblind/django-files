# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.core import urlresolvers
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import DetailView, SingleObjectMixin,\
    BaseDetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView,\
    ModelFormMixin

from files.models import Attachment
from files.forms import AttachmentForm
from django.core.urlresolvers import NoReverseMatch
from django.template.defaultfilters import slugify


class AttachmentPostBadRequest(HttpResponseBadRequest):
    """
    Response returned when an attachment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(AttachmentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("attachments/400-debug.html", {"why": why})


class AttachmentCreateView(CreateView):
    model = Attachment
    form_class = AttachmentForm
    
    def get_success_url(self):
        try:
            return super(AttachmentCreateView, self).get_success_url()
        except NoReverseMatch:
            # Since instance is saved, but not yet updated with data
            # from the `write_binary` raw sql method in the storage backend,
            # slugify the pre_slug (which is unique at this stage,
            # and will resolve to the correct slug).
            self.object.slug = slugify(self.object.pre_slug)
        finally:
            return super(AttachmentCreateView, self).get_success_url()
    
    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        try:
            data = kwargs["data"]
            ctype_pk, object_pk = data["content_type"], data["object_id"]
            ctype = ContentType.objects.get_for_id(ctype_pk)
            obj = ctype.get_object_for_this_type(pk=object_pk)
        except KeyError, e:
            return AttachmentPostBadRequest(e.args[0])
        return form_class(obj, **kwargs)
    
    def form_valid(self, form):
        # Set some additional attributes
        form.instance.creator = self.request.user
        form.instance.ip_address = self.request.META["REMOTE_ADDR"]
        return super(AttachmentCreateView, self).form_valid(form)
    

class AttachmentEditView(UpdateView, ModelFormMixin):
    model = Attachment
#    success_url = urlresolvers.reverse("edited")


class AttachmentDetailView(DetailView):
    """
    Returns the details of an attachment.
    """
    model = Attachment
    context_object_name = "attachment"
    template_name = "attachments/view.html"
    

class AttachmentDeleteView(DeleteView):
    model = Attachment


class AttachmentDownloadView(BaseDetailView, SingleObjectMixin):
    """
    Returns the attachment file as a HttpResponse.
    """
    model = Attachment
    
    def render_to_response(self, context):
        obj = context["object"]
        response = HttpResponse(obj.attachment.file.read(), mimetype=obj.mimetype)
        response["Content-Disposition"] = "inline; filename=%s" % obj.filename
        return response
