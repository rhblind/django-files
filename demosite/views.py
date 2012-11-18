# Create your views here.

from django.views.generic import DetailView
from django.http import HttpResponse


def home(request):
    return HttpResponse("Home")
