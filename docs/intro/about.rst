About django-files
==================

This project is the result of a personal need for a more portable, consistent attachments system. As Django provides an excellent base for this through the `ContentTypes framework`_, and provides a great example for how to implement this in their `Comments framework`_, this proved to be an (almost) trivial task.


Features
--------

* Seamless integration with the existing FileSystemStorage backend
* Database storage bacends. This allows you to store files directly in the database. No manual configuration or creation of database tables are required (Only PostgreSQL and SQLite implemented so far).
* No unit tests whatsoever! This is completly untested code, no kidding!

.. todo::
    Write unit tests.

.. warning::
    Storing files in your database should be used with caution if you have lots of attachments. This might severly degrade your database performance. Storing files in your filesystem (after all, that's what filesystems do best) are much more efficient performance wise.

.. _ContentTypes framework: https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
.. _Comments framework: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
