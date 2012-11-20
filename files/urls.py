from django.conf.urls import patterns, url

from files.views import AttachmentCreateView, AttachmentDeleteView, \
    AttachmentDetailView, AttachmentDownloadView, AttachmentEditView

urlpatterns = patterns("files.views",
    url(r"^add/$", view=AttachmentCreateView.as_view(), name="add-attachment"),
    url(r"^view/(?P<slug>[-\w]+)/$", view=AttachmentDetailView.as_view(), name="view-attachment"),
    url(r"^edit/(?P<slug>[-\w]+)/$", view=AttachmentEditView.as_view(), name="edit-attachment"),
    url(r"^delete/(?P<slug>[-\w]+)/$", view=AttachmentDeleteView.as_view(), name="delete-attachment"),
    url(r"^download/(?P<slug>[-\w]+)/$", view=AttachmentDownloadView.as_view(), name="download-attachment"),
)
