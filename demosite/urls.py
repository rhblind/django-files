from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from demosite.views import ShapeListView

admin.autodiscover()

urlpatterns = patterns("demosite.views",
    url(r"^$", view=ShapeListView.as_view(), name="home"),
    url(r"^basic-usage/$", view=ShapeListView.as_view(template_name="basic-usage.html"), name="basic-usage"),
    url(r"^rendering/$", view=ShapeListView.as_view(template_name="rendering.html"), name="rendering"),
)
