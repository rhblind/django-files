.. _contents:

========================
Welcome to django-files!
========================

Thanks for checking out django-files.
This project aims to be an easy, portable, pluggable and maintainable attachment framework for Django.


.. toctree:
    :hidden:

    index
    

.. toctree::
    :maxdepth: 2

    intro/about
 


Installation
============

I have not yet been able to package django-files for pypi, so installation needs to be done by cloning from github. This is luckily a pretty painless process and can be done by following these steps.

.. code-block:: none

    $ git clone git://github.com/rhblind/django-files.git
    $ cd django-files
    $ python setup.py install

This will install django-files in your PYTHONPATH.

.. note::

    If you are using virtualenv, remember to activate your environment before running the setup script. If you are not, why not? You really should =)

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

You will also need to enable the `django.contrib.auth`, `django.contrib.contenttypes` and the `django.contrib.sites` apps, as they are used in the Attachment model.

.. autoclass:: models.Attachment


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

