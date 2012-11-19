from django.conf.urls import patterns, url

from files.views import AttachmentDetailView, AttachmentDownloadView

urlpatterns = patterns("files.views",
    url(r"^view/(?P<slug>[-\w]+)/$", view=AttachmentDetailView.as_view(), name="view-attachment"),
#    url(r"^add/(?P<pk>\d+)/$", view="", name="add-attachment"),
#    url(r"^delete/(?P<pk>\d+)/$", view="", name="delete-attachment"),
    url(r"^download/(?P<slug>[-\w]+)/$", view=AttachmentDownloadView.as_view(), name="download-attachment"),
)

