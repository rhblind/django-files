# -*- coding: utf-8 -*-

from django.views.generic.detail import DetailView, SingleObjectMixin,\
    BaseDetailView
from files.models import Attachment
from django.http import HttpResponse


class AttachmentDetailView(DetailView):
    """
    Returns the details of an attachment.
    """
    
    model = Attachment
    context_object_name = "attachment"
    template_name = "attachments/detail.html"


class AttachmentDownloadView(BaseDetailView, SingleObjectMixin):
    """
    Returns the attachment file as a HttpResponse.
    """
    
    model = Attachment
    
    def render_to_response(self, context):
        obj = context["object"]
        response = HttpResponse(obj.attachment.file, mimetype=obj.mimetype)
        response["Content-Disposition"] = "inline; filename=%s" % obj.attachment.file
        return response
