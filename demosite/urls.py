from django.contrib import admin
from django.conf.urls import patterns, url
from demosite.views import ShapeDetailView

admin.autodiscover()

urlpatterns = patterns(
    "demosite.views",
    url(r"^$", view=ShapeDetailView.as_view(), name="home"),
    url(r"^form-example/$", view=ShapeDetailView.as_view(template_name="form_example.html"),
        name="form_example"),
    url(r"^edit-form-example/$", view=ShapeDetailView.as_view(template_name="edit_form_example.html"),
        name="edit_form_example"),
    url(r"^formset-example/$", view=ShapeDetailView.as_view(template_name="formset_example.html"),
        name="formset_example"),
    url(r"^listing-and-counting-example/$", view=ShapeDetailView.as_view(template_name="listing_example.html"),
        name="listing_example"),
)
