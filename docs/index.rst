.. _index:

======================================
Welcome to django-files documentation!
======================================

Thanks for checking out django-files.
This :doc:`project<about>` aims to be an easy, portable, pluggable and maintainable attachments framework for Django.


See the :doc:`detailed table of contents <contents>` for specific information.

.. toctree::
    :maxdepth: 1

    about
    usage/basic

Installation
============

From the Python package index (pypi)
------------------------------------

.. code-block:: none

    $ pip install django-files

    OR

    $ easy_install django-files
    

From Git
--------

.. code-block:: none

    $ git clone git://github.com/rhblind/django-files.git
    $ cd django-files
    $ python setup.py install

This will install django-files in your PYTHONPATH.

.. note::

    If you are using virtualenv, remember to activate your environment before running the setup script.

Configuration
=============

After you have installed django-files in your PYTHONPATH, you need to add it to your INSTALLED_APPS in your django project.

.. code-block:: python

    ...
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sites',
        ...
        'files',    # django-files attachments framework
        ...
    )

You will also need to enable the `django.contrib.auth`, `django.contrib.contenttypes` and the `django.contrib.sites` apps, as they are used in the :class:`~files.models.Attachment` class.


Optional settings
=================

DEFAULT_FILE_STORAGE
--------------------

.. code-block:: python
    
    # Set the filesystem storage backend to use.
    
    DEFAULT_FILE_STORAGE = "files.storage.SQLiteStorage"

This option set what kind of file storage backend you would like to use. If omitted, the default is `django.core.files.storage.FileSystemStorage`.

Valid backends are:

* django.core.files.storage.FileSystemStorage
* files.storage.SQLiteStorage
* files.storage.PostgreSQLStorage

REQUIRE_AUTH_DOWNLOAD
---------------------

.. code-block:: python

    # If this is set to True, users are required to be
    # authenticated in addition to be have the "files.download_attachment"
    # permission to be able to download files. Default is False.

    REQUIRE_AUTH_DOWNLOAD = True


.. attention::

    The next two options has no effect if using a database storage backend, as the file is stored directly in the database and will be wiped away when the row is deleted.


FORCE_FILE_RENAME
-----------------

.. code-block:: python

    # If using the FileSystemStorage, setting this to True will
    # append a FORCE_FILE_RENAME_POSTFIX postfix on files in the filesystem which
    # has had their database reference deleted. Has no effect on
    # database storage backends. 
    
    FORCE_FILE_RENAME = True


FORCE_FILE_RENAME_POSTFIX
-------------------------

.. code-block:: python
    
    # Set this to whatever you want your removed files to be
    # appended with. Defaults to "_removed". This setting has no
    # effect on the database storage backends, as they are gently
    # killed.
    
    FORCE_FILE_RENAME_POSTFIX = "_removed"


ATTACHMENT_MAX_SIZE
-------------------

.. code-block:: python

    # Set the max allowed file size (in bytes) for attachments.
    # If not set, no file size restrictions will be enforced.
    # Note that this check will be performed after the file has
    # been uploaded into the memory. Please make sure to protect your
    # web server by setting (i.e. LimitRequestBody) to prevent uploading
    # big files in memory.
    
    ATTACHMENT_MAX_SIZE = 4194304  # 4 MB

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

