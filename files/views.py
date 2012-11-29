# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.template.context import RequestContext
from django.template.loader import render_to_string, select_template
from django.http import HttpResponse, HttpResponseBadRequest,\
    HttpResponseRedirect
from django.views.generic.detail import DetailView, SingleObjectMixin,\
    BaseDetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView

from files import get_form
from files.models import Attachment


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
    """
    View responsible for creating new attachments.
    """
    model = Attachment
    context_object_name = "attachment"
    form_class = get_form()
    template_name = "attachments/form.html"

    def get_form(self, form_class):
        # TODO: Better way to fetch object
        kwargs = self.get_form_kwargs()
        try:
            data = kwargs["data"]
            ctype_pk, object_pk = data["content_type"], data["object_id"]
            ctype = ContentType.objects.get_for_id(ctype_pk)
            obj = ctype.get_object_for_this_type(pk=object_pk)
        except KeyError, e:
            # FIXME: Does not work!
            return AttachmentPostBadRequest(e.args[0])
        return form_class(obj, **kwargs)
    
    def form_valid(self, form):
        # Set some additional attributes from request.
        form.instance.creator = self.request.user
        form.instance.ip_address = self.request.META["REMOTE_ADDR"]
        return super(AttachmentCreateView, self).form_valid(form)
    

class AttachmentEditView(UpdateView):
    """
    Updates an existing attachment with new data.
    """
    model = Attachment
    context_object_name = "attachment"
    form_class = get_form()
    
    def get_form(self, form_class):
        obj = self.object.content_type \
            .get_object_for_this_type(pk=self.object.object_id)
        return form_class(obj, **self.get_form_kwargs())

    def get_template_names(self):
        names = super(AttachmentEditView, self).get_template_names()
        if self.object:
            ctype = self.object.content_type
            template_search_list = [
                "attachments/%s/%s/edit_form.html" % (ctype.app_label, ctype.model),
                "attachments/%s/edit_form.html" % ctype.app_label,
                "attachments/%s/edit_form.html" % ctype.model,
                "attachments/edit_form.html"
            ]
            names = [p for p in template_search_list] + names
        return names


class AttachmentDetailView(DetailView):
    """
    Returns the details of an attachment.
    """
    model = Attachment
    context_object_name = "attachment"
    template_name = "attachments/view.html"
    

class AttachmentDeleteView(DeleteView):
    """
    Deletes an attachment from the storage backend.
    """
    model = Attachment
    context_object_name = "attachment"
    
    def get_template_names(self):
        """
        Add content type object app_name and model
        to template search path.
        """
        names = super(AttachmentDeleteView, self).get_template_names()
        if self.object:
            ctype = self.object.content_type
            template_search_list = [
                "attachments/%s/%s/delete.html" % (ctype.app_label, ctype.model),
                "attachments/%s/delete.html" % ctype.app_label,
                "attachments/%s/delete.html" % ctype.model,
                "attachments/delete.html"
            ]
            names = [p for p in template_search_list] + names
        return names
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        # If success_url is provided, redirect.
        # Else, render a default response using
        # either a default or custom template.
        if self.success_url:
            return HttpResponseRedirect(self.success_url)
        else:
            ctype = self.object.content_type
            template_search_list = [
                "attachments/%s/%s/deleted.html" % (ctype.app_label, ctype.model),
                "attachments/%s/deleted.html" % ctype.app_label,
                "attachments/%s/deleted.html" % ctype.model,
                "attachments/deleted.html"
            ]
            template = select_template(template_search_list)
            return render_to_response(template.name, self.get_context_data(), RequestContext(request))
    
    
class AttachmentDownloadView(BaseDetailView, SingleObjectMixin):
    """
    Returns the attachment file as a HttpResponse.
    """
    model = Attachment
    context_object_name = "attachment"
    
    def render_to_response(self, context):
        obj = context["object"]
        response = HttpResponse(obj.attachment.file.read(), mimetype=obj.mimetype)
        response["Content-Disposition"] = "inline; filename=%s" % obj.filename
        return response
