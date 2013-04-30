# Create your views here.

from django.views.generic import DetailView
from demosite.models import Shape


class ShapeDetailView(DetailView):
    """
    The view
    """

    model = Shape
    template_name = "home.html"

    def get_object(self, queryset=None):

        try:
            obj = super(ShapeDetailView, self).get_object(queryset)
        except AttributeError:
            obj, created = Shape.objects.get_or_create(**{
                "color": "green",
                "shape": "square",
                "descr": "A green square"
            })
        finally:
            return obj
