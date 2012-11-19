# -*- coding: utf-8 -*-

import os
import re
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import get_storage_class

from files.utils import md5buffer
from files.signals import write_binary, unlink_binary


def get_upload_to(instance, filename):
    """
    Get the path which should be appended to MEDIA_ROOT to
    determine the value of the url attribute.
    """
    prefix = getattr(settings, "FILE_STORAGE_PREFIX", "attachments")
    app_model = u"_".join((instance.content_object._meta.app_label,
                          instance.content_object._meta.object_name)).lower()
    return u"/".join(map(str, (prefix, app_model, instance.content_object.pk, filename)))


class BlobField(models.Field):
    """
    Represents a Binary Large OBject field in the database.
    """

    description = _("Binary large object (blob) field")
    
    def get_internal_type(self):
        return "BlobField"

    def db_type(self, connection):
        """
        Figure out what storage backend we're running on,
        and return correct field type for this backend.
        """
        vendor_blob_name = {
            "sqlite": "blob",
            "mysql": "blob",
            "oracle": "blob",
            "postgresql": "oid"
        }
        return vendor_blob_name[connection.vendor]


class AttachmentManager(models.Manager):
    """
    Manager for attachments
    """
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_models(obj)
        return self.get_query_set().filter(content_type__pk=object_type.pk, object_id=obj.pk)
        

class BaseAttachmentAbstractModel(models.Model):
    """
    An abstract model that any custom attachment model should
    subclass.
    """
    
    # Content object fields
    content_type = models.ForeignKey(ContentType,
                    verbose_name=_("content type"),
                    related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")

    # Some metadata fields
    site = models.ForeignKey(Site, default=Site.objects.get_current)
    ip_address = models.IPAddressField(_("IP address"), blank=True, null=True)
    is_public = models.BooleanField(_("is public"), default=True,
                    help_text=_("Uncheck to hide the attachment from other users"))
    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)
    
    class Meta:
        abstract = True


class Attachment(BaseAttachmentAbstractModel):
    """
    A file attached to some object.
    """
    
    creator = models.ForeignKey(User, related_name="created_attachments", verbose_name=_("creator"))
    description = models.CharField(_("description"), max_length=100, blank=True, null=True)
    attachment = models.FileField(_("attachment"), upload_to=get_upload_to, db_index=True)
    blob = BlobField(_("binary data"), blank=True, null=True, editable=False)
    backend = models.CharField(max_length=100, editable=False,
                               default=lambda: str(get_storage_class().__name__))
    
    # Metadata about the file
    mimetype = models.CharField(_("mime type"), max_length=50, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, editable=False)
    size = models.PositiveIntegerField(_("file size"), blank=True, editable=False)
    checksum = models.CharField(_("md5 checksum"), max_length=32, blank=True, editable=False)
    
    # Manager
    objects = AttachmentManager()
    
    class Meta:
        ordering = ("created", "modified")
        permissions = (
            ("delete_other_attachment", "Can delete other attachment"),
        )
        
    def __unicode__(self):
        return u"%s attached by %s" % (self.filename, self.creator)
    
    @models.permalink
    def get_absolute_url(self):
        return ("view-attachment", (), {"slug": self.slug})
    
    def clean(self):
        """
        This method is called before each save.
        """
        self.size = self.attachment.size
        if hasattr(self.attachment.file, "content_type"):
            self.mimetype = self.attachment.file.content_type
        
    def save(self, *args, **kwargs):
        """
        Check what storage backend which are being used.
        If backend is any of the provided database backends,
        emit the `write_binary` signal to write the file to
        the blob field.
        """
        if self.backend in ["PostgreSQLStorage", "MySQLStorage", "SQLiteStorage", "OracleStorage"]:
            # If using one of the included database backends,
            # save the instance and emit the `write_binary` signal
            # to write the binary data into the blob field.
            try:
                inmem_file = self.attachment.file or self.blob
                super(Attachment, self).save(*args, **kwargs)
                write_binary.send(sender=Attachment, instance=self, content=inmem_file)
            except Exception:
                raise
        else:
            super(Attachment, self).save(*args, **kwargs)
    
    def delete(self, using=None):
        """
        Emit the `unlink_binary` signal to perform extra
        work before removing if required by backend.
        """
        unlink_binary.send(sender=Attachment, instance=self)
        super(Attachment, self).delete(using=using)
    
    @property
    def pre_slug(self):
        """
        Create a nice "semi unique" slug. This is not the real slug,
        only a helper method to create the string which is slugified.
        """
        s = "-".join(map(str, (self.content_type, self.pk, os.path.basename(self.attachment.name))))
        return re.sub("[^\w+]", "-", s)
    
    @property
    def filename(self):
        return os.path.basename(self.attachment.name)
    
    @property
    def checksum_match(self):
        """
        If this is False, something fishy is going on.
        """
        cksum = md5buffer(self.blob)
        return cksum == self.checksum


#
# Call the clean() method on pre_save
# to set some attributes based on the uploaded
# file.

@receiver(signals.pre_save, sender=Attachment)
def clean_attachment_callback(sender, instance, **kwargs):
    instance.clean()
