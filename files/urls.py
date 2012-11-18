from django.conf.urls import patterns, url

from files.views import AttachmentDetailView

urlpatterns = patterns("files.views",
    url(r"^view/(?P<slug>[-\w]+)/$", view=AttachmentDetailView.as_view(), name="view-attachment"),
#    url(r"^add/(?P<pk>\d+)/$", view="", name="add-attachment"),
#    url(r"^delete/(?P<pk>\d+)/$", view="", name="delete-attachment"),
#    url(r"^download/(?P<pk>\d+)/$", view="", name="download-attachment")
    
# From bartTC
#    url(r'^add-for/(?P<app_label>[\w\-]+)/(?P<module_name>[\w\-]+)/(?P<pk>\d+)/$', 'attachments.views.add_attachment', name="add_attachment"),
#    url(r'^delete/(?P<attachment_pk>\d+)/$', 'attachments.views.delete_attachment', name="delete_attachment"),
)
