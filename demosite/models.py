from django.db import models
from django.utils.translation import ugettext_lazy as _


class Shape(models.Model):
    
    SHAPES = (
        (u"square", u"Square"),
        (u"rectangle", u"Rectangle"),
        (u"triangle", u"Triangle")
    )
    
    COLORS = (
        (u"red", u"Red"),
        (u"blue", u"Blue"),
        (u"green", u"Green"),
        (u"yellow", u"Yellow")
    )
    
    shape = models.CharField(max_length=10, choices=SHAPES)
    color = models.CharField(max_length=10, choices=COLORS)
    descr = models.TextField(_("description"), blank=True, null=True)
    
    class Meta:
        unique_together = ["color", "shape"]
    
    def __unicode__(self):
        return u"%s %s" % (self.color, self.shape)
