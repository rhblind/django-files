# -*- coding: utf-8 -*-

from __future__ import absolute_import

from files.models import Attachment
from files.forms import AttachmentForm

from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

DEFAULT_FILE_STORAGE_BACKEND = "django.core.files.storage.FileSystemStorage"
CONTRIB_BACKENDS = [
    DEFAULT_FILE_STORAGE_BACKEND,
    "files.storage.SQLiteStorage",
    "files.storage.PostgreSQLStorage",
    "files.storage.MySQLStorage",
    "files.storage.OracleStorage",
]


def get_storage_backend():
    """
    Get the file storage backend (i.e. "django.core.files.storage.FileSystemStorage")
    as defined in settings.py.
    """
    # Make sure the backend is in INSTALLED_APPS
    backend = get_storage_backend_name()
    app_name = ".".join(backend.split(".")[:1])
    if app_name not in settings.INSTALLED_APPS and backend != DEFAULT_FILE_STORAGE_BACKEND:
        # Don't raise if default storage as this is the default fallback,
        # and does not has to specified in settings.py.
        raise ImproperlyConfigured("The DEFAULT_FILE_STORAGE (%r) must be in INSTALLED_APPS" % settings.DEFAULT_FILE_STORAGE)
    
    # Try to import the package
    try:
        module = import_module(app_name)
    except ImportError:
        raise ImproperlyConfigured("The DEFAULT_FILE_STORAGE settings refers to a non-existing package")
    
    return module


def get_storage_backend_name():
    """
    Returns the name of the storage backend (either the settings value,
    if it exists, or the default).
    """
    return getattr(settings, "DEFAULT_FILE_STORAGE", DEFAULT_FILE_STORAGE_BACKEND)


def get_model():
    """
    Returns the attachment model class.
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_model"):
        return get_storage_backend().get_model()
    else:
        return Attachment
    
    
def get_form():
    """
    Returns the attachment ModelForm class
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_form"):
        return get_storage_backend().get_form()
    else:
        return AttachmentForm


def get_create_target():
    """
    Returns the target URL for the attachment form submission view
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_create_target"):
        return get_storage_backend().get_create_target()
    else:
        return urlresolvers.reverse("add-attachment")


def get_view_url(attachment):
    """
    Get the URL for the "view this attachment" view
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_view_url"):
        return get_storage_backend().get_view_url(attachment)
    else:
        return urlresolvers.reverse("view-attachment", kwargs={"slug": attachment.slug})


def get_edit_url(attachment):
    """
    Get the URL for the "edit this attachment" view
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_edit_url"):
        return get_storage_backend().get_edit_url(attachment)
    else:
        return urlresolvers.reverse("edit-attachment", kwargs={"slug": attachment.slug})


def get_delete_url(attachment):
    """
    Get the URL for the "delete this attachment" view
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_delete_url"):
        return get_storage_backend().get_delete_url(attachment)
    else:
        return urlresolvers.reverse("delete-attachment", kwargs={"slug": attachment.slug})


def get_download_url(attachment):
    """
    Get the download URL for this attachment
    """
    if get_storage_backend_name() not in CONTRIB_BACKENDS and hasattr(get_storage_backend(), "get_download_url"):
        return get_storage_backend().get_download_url(attachment)
    else:
        return urlresolvers.reverse("download-attachment", kwargs={"slug": attachment.slug})
