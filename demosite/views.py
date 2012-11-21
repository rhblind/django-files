# Create your views here.

from django.views.generic.list import ListView
from demosite.models import Shape


class ShapeListView(ListView):
    model = Shape
    context_object_name = "shapes"
    template_name = "home.html"
