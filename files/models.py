# -*- coding: utf-8 -*-

import os
import re
import errno
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.core.files.storage import get_storage_class

from files.utils import md5buffer
from files.signals import write_binary, unlink_binary, post_write, post_unlink
from django.core.exceptions import ValidationError


def get_upload_to(instance, filename):
    """
    Get the path which should be appended to MEDIA_ROOT to
    determine the value of the url attribute.
    """
    prefix = getattr(settings, "FILE_STORAGE_PREFIX", "attachments")
    app_model = u"_".join((instance.content_object._meta.app_label,
                          instance.content_object._meta.object_name)).lower()
    return u"/".join(map(str, (prefix, app_model, instance.content_object.pk, filename)))


class UnsupportedBackend(Exception):
    pass


class BlobField(models.Field):
    """
    Represents a Binary Large Object field in the database.
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
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"),
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
            ("delete_all_attachment", "Can delete all attachment"),
            ("download_attachment", "Can download attachment"),
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
        try:
            self.size = self.attachment.size
            if hasattr(self.attachment.file, "content_type"):
                self.mimetype = self.attachment.file.content_type
        except ValueError, e:
            raise ValidationError(e.args[0])
        
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
                content = self.attachment.file
                super(Attachment, self).save(*args, **kwargs)
                write_binary.send(sender=Attachment, instance=self, content=content)
            except Exception, e:
                raise e
        elif self.backend == "FileSystemStorage":
            # If using the default FileSystemStorage,
            # save some extra attributes as well.
            if not self.pk:
                super(Attachment, self).save(*args, **kwargs)
            self.slug = slugify(self.pre_slug)
            self.checksum = md5buffer(self.attachment.file)
            super(Attachment, self).save(force_update=True)
        else:
            raise UnsupportedBackend("Unsupported storage backend.")
        # Send the post_write signal after save even if backend does not
        # use the write_binary method (such as the FileStorageBackend), to
        # keep consistancy between all backends.
        post_write.send(sender=Attachment, instance=self)
    
    @property
    def pre_slug(self):
        """
        Create a nice "semi unique" slug. This is not the real slug,
        only a helper method to create the string which is slugified.
        """
        s = "-".join(map(str, (self.content_type, self.pk,
                               os.path.basename(self.attachment.name))))
        return re.sub("[^\w+]", "-", s)
    
    @property
    def filename(self):
        return os.path.basename(self.attachment.name)
    
    @property
    def checksum_match(self):
        """
        If this is False, something fishy is going on.
        """
        return md5buffer(self.attachment.file) == self.checksum


#
# Signals
#

@receiver(signals.pre_save, sender=Attachment)
def pre_save_callback(sender, instance, **kwargs):
    """
    Run clean before each save to set some values
    based on the uploaded attachment.
    """
    instance.clean()


@receiver(signals.post_save, sender=Attachment)
def post_save_callback(sender, instance, created, **kwargs):
    """
    Sets a _created flag on the attachment instance to indicate
    that this is a new attachment.
    """
    if created:
        instance._created = True


@receiver(signals.pre_delete, sender=Attachment)
def pre_delete_callback(sender, instance, **kwargs):
    """
    Emits the `unlink_binary` signal to perform extra
    work before removing the attached file if required by backend.
    """
    unlink_binary.send(sender=Attachment, instance=instance)
    post_unlink.send(sender=Attachment, instance=instance)


@receiver(signals.post_delete, sender=Attachment)
def post_delete_callback(sender, instance, **kwargs):
    """
    The FileStorage backend does not remove files when the
    reference is deleted, to avvoid data loss.
    If settings.FORCE_FILE_RENAME = True, rename the file
    to <filename.ext>_removed to indicate that this file is
    removed from the database.
    """
    if instance.backend == "FileSystemStorage":
        rename = getattr(settings, "FORCE_FILE_RENAME", False)
        if rename is True:
            # Rename the file to indicate removal of database reference.
            # There is a race condition between os.path.exists and os.rename:
            # If os.rename fails with ENOENT, the file does not exist anymore,
            # and we continue as usual.
            name = os.path.join(instance.attachment.storage.location, instance.attachment.name)
            if os.path.exists(name):
                try:
                    new_name = "".join((name,
                         getattr(settings, "FORCE_FILE_RENAME_POSTFIX", "_removed")))
                    os.rename(name, new_name)
                except OSError, e:
                    if e.errno != errno.ENOENT:
                        raise e
