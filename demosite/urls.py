from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from demosite.views import ShapeListView

admin.autodiscover()

urlpatterns = patterns("demosite.views",
    url(r"^$", view=ShapeListView.as_view(), name="home"),
    url(r"^wizard1/$", view=ShapeListView.as_view(template_name="wizard1.html"), name="wiz1"),
    url(r"^wizard2/$", view=ShapeListView.as_view(template_name="wizard2.html"), name="wiz2"),
    url(r"^wizard3/$", view=ShapeListView.as_view(template_name="wizard3.html"), name="wiz3"),
    url(r"^wizard4/$", view=ShapeListView.as_view(template_name="wizard4.html"), name="wiz4"),
)
