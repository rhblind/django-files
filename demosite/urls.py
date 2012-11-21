from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from demosite.views import ShapeListView

admin.autodiscover()

urlpatterns = patterns("demosite.views",
    url(r"^$", view=ShapeListView.as_view(), name="home"),
)
