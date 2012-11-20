# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _, ungettext

from files.models import Attachment


class AttachmentAdmin(admin.ModelAdmin):
    """
    A generic admin form for attachments
    """
    readonly_fields = ("mimetype", "slug", "size", "checksum", "ip_address",
                       "backend", "created", "modified")
    fieldsets = [
        (None, {"fields": ("creator", "description", "attachment", "site", "is_public",
                           "slug", "backend", "ip_address")}),
        ("Object relations", {"fields": ("content_type", "object_id")}),
        ("Metadata", {"fields": ("mimetype", "size", "checksum", "created", "modified")})
    ]
    list_display = ("attachment", "mimetype", "content_type", "object_id", "is_public",
                    "created", "ip_address", "site")
    ordering = ("-created", "content_type")
    actions = ["set_is_public", "set_is_private"]
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not obj.pk:
            # Only save ip_address for new objects
            obj.ip_address = request.META["REMOTE_ADDR"]
        super(AttachmentAdmin, self).save_model(request, obj, form, change)
            
    #
    # Actions
    #
    def get_actions(self, request):
        actions = super(AttachmentAdmin, self).get_actions(request)
        # Only superusers should be able to delete attachments from
        # the admin interface.
        if not request.user.is_superuser and "delete_selected" in actions:
            actions.pop("delete_selected")
        if not request.user.has_perm("files.change_attachment"):
            if "set_is_public" in actions:
                actions.pop("set_is_public")
            if "set_is_private" in actions:
                actions.pop("set_is_public")
        return actions
    
    def set_is_public(self, request, queryset):
        queryset.update(is_public=True)
        self._display_message(request, queryset,
                  lambda n: ungettext("marked public", "marked public", n))
    set_is_public.short_description = _("Mark selected attachments as public")
    
    def set_is_private(self, request, queryset):
        queryset.update(is_public=False)
        self._display_message(request, queryset,
                  lambda n: ungettext("marked private", "marked private", n))
    set_is_private.short_description = _("Mark selected attachments as private")
    
    def _display_message(self, request, queryset, message):
        n = queryset.count()
        msg = ungettext(u"1 comment was successfully %(action)s.",
                        u"%(count)s comments were successfully %(action)s.", n)
        self.message_user(request, msg % {"count": n, "action": message(n)})
    

class AttachmentInlines(generic.GenericStackedInline):
    """
    A generic stacked inline admin form which can be used
    to display attachments for the various models they are
    attached to.
    
    To enable in the admin interface, add it to the model
    like this.
    
    Syntax::
        from files.admin import AttachmentInlines
    
        class MyModel(admin.ModelAdmin):
            
            inlines = [AttachmentInlines]
            
            
    """
    model = Attachment
    readonly_fields = ("mimetype", "slug", "size", "checksum", "ip_address", "backend",
                       "created", "modified")
    fieldsets = [
        (None, {"fields": ("creator", "description", "attachment", "site", "is_public",
                           "slug", "backend", "ip_address")}),
        ("Metadata", {"fields": ("mimetype", "size", "checksum", "created", "modified"),
                      "classes": ("collapse", )})
    ]
    extra = 1
    

admin.site.register(Attachment, AttachmentAdmin)