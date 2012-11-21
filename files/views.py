# -*- coding: utf-8 -*-

from django.views.generic.detail import DetailView, SingleObjectMixin,\
    BaseDetailView
from files.models import Attachment
from django.http import HttpResponse
from django.views.generic.edit import DeleteView, CreateView, UpdateView


class AttachmentCreateView(CreateView):
    model = Attachment


class AttachmentDetailView(DetailView):
    """
    Returns the details of an attachment.
    """
    model = Attachment
    context_object_name = "attachment"
    template_name = "attachments/view.html"


class AttachmentEditView(UpdateView):
    model = Attachment


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
    


