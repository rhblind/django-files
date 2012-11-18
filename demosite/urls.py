from django.contrib import admin
from django.conf.urls.defaults import patterns, url

admin.autodiscover()

urlpatterns = patterns("demosite.views",
    url(r"^$", view="home", name="home"),
)
