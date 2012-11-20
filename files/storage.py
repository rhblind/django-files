# -*- coding: utf-8 -*-

import urlparse
import itertools
from StringIO import StringIO
from django.conf import settings
from django.db import connections, transaction
from django.core import urlresolvers
from django.core.files.storage import Storage, get_storage_class
from django.core.files.base import File
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify

from files.utils import md5buffer
from files.models import Attachment
from files.forms import AttachmentForm
from files.signals import write_binary, unlink_binary


class DatabaseStorage(Storage):
    """
    This is a storage backend which saves attachments as binary data
    in a database.
    
    The database storage backend expects a table as such:
    
        table name:        dbstorage
        columns:
            id:            int(4), pk not null
            fname_blob:    blob, not null
            fname:         varchar(100), not null index
            size:          int(8), not null
            created:       datetime, not null
            modified:      datetime, not null
    
    """
    def __init__(self, using=None, base_url=None):
        self.using = using or "default"
        self.base_url = base_url or getattr(settings, "MEDIA_URL", "")
    
    def _open(self, name, mode="rb"):
        """
        This method is called by Storage.open(),
        and should be overridden to provide
        correct SQL syntax for current databas engine
        
        Must return a File() object
        """
        pass
    
    def _save(self, name, content):
        """
        This method is called by Storage.save(),
        and should be overridden to provide
        correct syntax for current database engine
        
        Must return name
        """
        pass
    
    def delete(self, name):
        """
        This method should be overridden to
        correctly deal with unlinking and deleting blob objects
        in current database engine if necessary.
        """
        pass
    
    #
    # The following methods should work on
    # all backends
    #
    
    def listdir(self, path):
        """
        This database backend does not support
        listing directories
        """
        raise NotImplementedError("Can't list directories from database backend.")
    
    def exists(self, name):
        return Attachment.objects.using(self.using).filter(attachment__exact=name).exists()
    
    def get_available_name(self, name):
        """
        Return a filename based on the name parameter that's
        free and available for new content to be written to
        on target storage system
        """
        # TODO: This is too expensive, and requires a new database lookup
        # on each iteration. Implement some caching method, or search through
        # a lazy queryset
        name = name.replace("\\", "/")
        count = itertools.count(1)

        while self.exists(name):
            namelist = name.split("/")
            dir_name, file_name = "/".join(namelist[:-1]), namelist[-1:][0]
            file_root, file_ext = file_name.split(".")
            name = "/".join((dir_name, "%s_%s.%s")) % (file_root, count.next(), file_ext)
        return name
    
    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace("\\", "/")
    
    def size(self, name):
        row = Attachment.objects.using(self.using).get(attachment__exact=name)
        return row.size
        
    def accessed_time(self, name):
        raise NotImplementedError("Access time is not tracked in database storage")
    
    def created_time(self, name):
        row = Attachment.objects.using(self.using).get(attachment__exact=name)
        return row.created
        
    def modified_time(self, name):
        row = Attachment.objects.using(self.using).get(attachment__exact=name)
        return row.modified
        

class PostgreSQLStorage(DatabaseStorage):
    """
    This is the database storage for PostgreSQL databases
    """
    def __init__(self, using=None, base_url=None):
        super(PostgreSQLStorage, self).__init__(using, base_url)
        
        raise NotImplementedError("Support for PostgreSQL databases is not yet implemented.")
    
    def _unlink_binary(self, instance):
        """
        Unlink the binary data before deleting
        """
        pass


class MySQLStorage(DatabaseStorage):
    """
    This is the database storage for MySQL databases
    """
    def __init__(self, using=None, base_url=None):
        super(MySQLStorage, self).__init__(using, base_url)
        
        raise NotImplementedError("Support for MySQL databases is not yet implemented.")


class SQLiteStorage(DatabaseStorage):
    """
    This is the database storage for SQLite databases
    """
    def __init__(self, using=None, base_url=None):
        super(SQLiteStorage, self).__init__(using, base_url)
        
    def _open(self, name, mode="rb"):
        """
        Return a File object.
        """
        row = Attachment.objects.using(self.using).get(attachment__exact=name)
        f = File(StringIO(row.blob), row.filename)
        f.size = row.size
        f.mode = mode
        return f
    
    def _save(self, name, content):
        """
        Do nothing.
        We are calling a special `write_binary` signal
        in the Attachment save() method, which will call the `_write_binary()`
        method below, and write the binary file into the Attachment row.
        """
        return name
    
    def _delete(self, name):
        """
        Remove the blob field from the row.
        """
        try:
            row = Attachment.objects.using(self.using).get(attachment__exact=name)
            row.blob = None
            row.save()
        except Attachment.DoesNotExist:
            # If not the attachment row exists,
            # do nothing.
            pass
        except Exception, e:
            raise e
        
    def _write_binary(self, instance, content):
        """
        Do the actual writing of binary data to the table.
        This method is called after the model has been saved,
        and can therefore be used to insert data based on
        information which was not accessible in the save method
        on the model.
        """
        import sqlite3
        cursor = connections[self.using].cursor()
        if isinstance(content, buffer):
            # If the content is a buffer object, this is an already
            # existing attachment. Check if the content has changed.
            cursor.execute("select checksum from files_attachment where id = %s", (instance.pk, ))
            new, orig = md5buffer(content), cursor.fetchone()[0]
            if new == orig:
                return
            else:
                blob = sqlite3.Binary(content)
        else:
            blob = sqlite3.Binary(content.file.read())

        slug = slugify(instance.pre_slug)
        checksum = md5buffer(blob)
        cursor.execute("update files_attachment set blob = %s, slug = %s, \
                        checksum = %s where id = %s",
                       (blob, slug, checksum, instance.pk))
        transaction.commit_unless_managed(using=self.using)


class OracleStorage(DatabaseStorage):
    """
    This is the database storage for Oracle databases
    """
    def __init__(self, using=None, base_url=None):
        super(OracleStorage, self).__init__(using, base_url)
        
        raise NotImplementedError("Support for Oracle databases is not yet implemented.")


#
# These methods are used by the template tags
#

def get_model():
    """
    Returns the model for this storage backend.
    """
    return Attachment


def get_form():
    """
    Returns the model form for this backend.
    """
    return AttachmentForm


def get_form_target():
    """
    Returns the URL for the add attachment view
    """
    return urlresolvers.reverse("add-attachment")


def get_delete_url(attachment):
    """
    Returns the URL for the delete attachment view
    """
    return urlresolvers.reverse("delete-attachment", kwargs={"slug": attachment.slug})


def get_edit_url(attachment):
    """
    Returns the URL for the edit attachment view
    """
    return urlresolvers.reverse("edit-attachment", kwargs={"slug": attachment.slug})


#
# Signals
# The write_binary signal is called from the Attachment's
# save() method, and is used to write the file into the blob
# field.
#

@receiver(write_binary, sender=Attachment)
def write_binary_callback(sender, instance, content, **kwargs):
    storage = get_storage_class()(instance._state.db, instance.attachment.url)
    storage._write_binary(instance, content)


@receiver(unlink_binary, sender=Attachment)
def unlink_binary_callback(sender, instance, **kwargs):
    storage = get_storage_class()(instance._state.db, instance.attachment.url)
    if hasattr(storage, "_unlink_binary"):
        storage._unlink_binary(instance)
