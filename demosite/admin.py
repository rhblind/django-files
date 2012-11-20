from django.contrib import admin
from demosite.models import Shape
from files.admin import AttachmentInlines


class ShapeAdmin(admin.ModelAdmin):
    inlines = [AttachmentInlines]
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            # Always save IP address of changed objects
            obj.ip_address = request.META["REMOTE_ADDR"]
            obj.save()
        formset.save_m2m()
        
    
admin.site.register(Shape, ShapeAdmin)
#admin.site.register(Shape)