# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseBadRequest
from django.core import urlresolvers
from django.views.generic.detail import DetailView, SingleObjectMixin,\
    BaseDetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView,\
    ModelFormMixin
from django.contrib.contenttypes.models import ContentType

from files.models import Attachment
from files.forms import AttachmentForm


class AttachmentCreateView(CreateView):
    model = Attachment
    form_class = AttachmentForm
#    template_name = "attachments/form.html"
    
    def get_template_names(self):
        names = ["", ""]
        return names
    
    def get_success_url(self):
        s = self.object.slug
        return urlresolvers.reverse("view-attachment", kwargs={"slug": self.object.slug})
    
    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        try:
            data = kwargs["data"]
            ctype_pk, object_pk = data["content_type"], data["object_id"]
            ctype = ContentType.objects.get_for_id(ctype_pk)
            obj = ctype.get_object_for_this_type(pk=object_pk)
        except KeyError:
            # TODO: handle this
            return HttpResponseBadRequest()
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
