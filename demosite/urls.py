from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from demosite.views import ShapeListView

admin.autodiscover()

urlpatterns = patterns("demosite.views",
    url(r"^$", direct_to_template, {"template": "home.html"}),
    url(r"^shapes/$", view=ShapeListView.as_view(), name="shapelist"),
)
