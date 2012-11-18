# -*- coding: utf-8 -*-

from django.views.generic.detail import DetailView
from files.models import Attachment


class AttachmentDetailView(DetailView):
    
    model = Attachment
    context_object_name = "attachment"
    template_name = "attachments/detail.html"
