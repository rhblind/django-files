# -*- coding: utf-8 -*-

import os
import urlparse
import itertools
from StringIO import StringIO
from django.conf import settings
from django.db import connections, transaction, IntegrityError
from django.core import urlresolvers
from django.core.files.base import File
from django.core.files.storage import Storage, get_storage_class
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify

from files.utils import md5buffer
from files.models import Attachment
from files.signals import write_binary, unlink_binary


class DatabaseStorage(Storage):
    """
    Database storage backend base.
    """
    def __init__(self, using=None, base_url=None):
        self.using = using or "default"
        self.base_url = base_url or getattr(settings, "MEDIA_URL", "")
    
    #
    # These methods _must_ be overridden by subclasses.
    #
    
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
    
    # The following methods should work on
    # all backends
    
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
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)

        count = itertools.count(1)
        while self.exists(name):
            # FIXME: This is a bit expensive, and requires a new database lookup
            # on each iteration.
            name = os.path.join(dir_name, "%s_%s%s" % (file_root, count.next(), file_ext))
        return name
    
    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace("\\", "/")
    
    def size(self, name):
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        return attachment.size
        
    def accessed_time(self, name):
        raise NotImplementedError("Access time is not tracked in database storage")
    
    def created_time(self, name):
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        return attachment.created
        
    def modified_time(self, name):
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        return attachment.modified
        

class PostgreSQLStorage(DatabaseStorage):
    """
    This is the database storage for PostgreSQL databases
    """
    def __init__(self, using=None, base_url=None):
        super(PostgreSQLStorage, self).__init__(using, base_url)
        
    def url(self, name):
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        if not attachment.slug:
            # If the slug field is empty, this attachment has just been
            # saved, but has not yet executed the `write_binary` signal.
            # Fall back to the super url.
            return super(PostgreSQLStorage, self).url(name)
        return urlresolvers.reverse("download-attachment", kwargs={"slug": attachment.slug})
    
    def _open(self, name, mode="rb"):
        """
        Read the file from the database, and return
        as a File instance.
        """
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        cursor = connections[self.using].cursor()
        lobject = cursor.db.connection.lobject(attachment.blob, "r")
        fname = File(StringIO(lobject.read()), attachment.filename)
        lobject.close()
        
        # Make sure the checksum match before returning the file
        if not md5buffer(fname) == attachment.checksum:
            raise IntegrityError("Checksum mismatch")
        
        fname.size = attachment.size
        fname.mode = mode
        
        return fname
    
    def _save(self, name, content):
        """
        Do nothing.
        We are calling a special `write_binary` signal
        in the Attachment save() method, which will call the `_write_binary()`
        method below, and write the binary file into the Attachment row.
        """
        return name
    
    def _write_binary(self, instance, content):
        """
        Do the actual writing of binary data to the table.
        This method is called after the model has been saved,
        and can therefore be used to insert data based on
        information which was not accessible in the save method
        on the model.
        """
        cursor = connections[self.using].cursor()
        if not (hasattr(instance, "_created") and instance._created is True):
            cursor.execute("select checksum from files_attachment where id = %s", (instance.pk, ))
            new, orig = md5buffer(content), cursor.fetchone()[0]
            if new == orig:
                return

        # If still here, either the file is a new upload,
        # or it has changed. In either case, write the
        # file to the database
        content.seek(0)
        blob_data = content.read()
        instance.slug = slugify(instance.pre_slug)
        instance.checksum = md5buffer(content)
        
        try:
            sid = transaction.savepoint(self.using)
            lobject = cursor.db.connection.lobject(0, "n", 0, None)
            lobject.write(blob_data)
            cursor.execute("update files_attachment set blob = %s, slug = %s, \
                            checksum = %s where id = %s", (lobject.oid, instance.slug,
                                                           instance.checksum, instance.pk))
            lobject.close()
            transaction.savepoint_commit(sid, using=self.using)
        except IntegrityError, e:
            transaction.savepoint_rollback(sid, using=self.using)
            raise e

    def _unlink_binary(self, instance):
        """
        Unlink the binary data before deleting
        """
        cursor = connections[self.using].cursor()
        try:
            sid = transaction.savepoint(self.using)
            lobject = cursor.db.connection.lobject(instance.blob, "w")
            lobject.unlink()
            lobject.close()
            transaction.savepoint_commit(sid, using=self.using)
        except IntegrityError, e:
            transaction.savepoint_rollback(sid, using=self.using)
            raise e


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
    
    def url(self, name):
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        if not attachment.slug:
            # If the slug field is empty, this attachment has just been
            # saved, but has not yet executed the `write_binary` signal.
            # Fall back to the super url.
            return super(SQLiteStorage, self).url(name)
        return urlresolvers.reverse("download-attachment", kwargs={"slug": attachment.slug})
       
    def _open(self, name, mode="rb"):
        """
        Return a File object.
        """
        attachment = Attachment.objects.using(self.using).get(attachment__exact=name)
        fname = File(StringIO(attachment.blob), attachment.filename)
        
        # Make sure the checksum match before returning the file
        if not md5buffer(fname) == attachment.checksum:
            raise IntegrityError("Checksum mismatch")
        
        fname.size = attachment.size
        fname.mode = mode
        return fname
    
    def _save(self, name, content):
        """
        Do nothing.
        We are calling a special `write_binary` signal
        in the Attachment save() method, which will call the `_write_binary()`
        method below, and write the binary file into the Attachment row.
        """
        return name
    
    def _write_binary(self, instance, content):
        """
        Do the actual writing of binary data to the table.
        This method is called after the model has been saved,
        and can therefore be used to insert data based on
        information which was not accessible in the save method
        on the model.
        """
        cursor = connections[self.using].cursor()
        if not (hasattr(instance, "_created") and instance._created is True):
            cursor.execute("select checksum from files_attachment where id = %s", (instance.pk, ))
            new, orig = md5buffer(content), cursor.fetchone()[0]
            if new == orig:
                return
        
        # If still here, either the file is a new upload,
        # or it has changed. In either case, write the
        # file to the database.
        content.seek(0)
        blob_data = buffer(content.read())
        instance.slug = slugify(instance.pre_slug)
        instance.checksum = md5buffer(content)
        cursor.execute("update files_attachment set blob = %s, slug = %s, \
                        checksum = %s where id = %s", (blob_data, instance.slug, instance.checksum, instance.pk))
        transaction.commit_unless_managed(using=self.using)


class OracleStorage(DatabaseStorage):
    """
    This is the database storage for Oracle databases
    """
    def __init__(self, using=None, base_url=None):
        super(OracleStorage, self).__init__(using, base_url)
        
        raise NotImplementedError("Support for Oracle databases is not yet implemented.")


# Signals
# The write_binary signal is called from the Attachment's
# save() method, and is used to write the file into the blob
# field.
# The unlink_binary signal is called on Attachment pre_delete
# to handle unlinking of the blob field if required.

@receiver(write_binary, sender=Attachment)
def write_binary_callback(sender, instance, content, **kwargs):
    storage = get_storage_class()(instance._state.db, instance.attachment.url)
    storage._write_binary(instance, content)


@receiver(unlink_binary, sender=Attachment)
def unlink_binary_callback(sender, instance, **kwargs):
    storage = get_storage_class()(instance._state.db, instance.attachment.url)
    if hasattr(storage, "_unlink_binary"):
        storage._unlink_binary(instance)
