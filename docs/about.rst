About django-files
==================

This project is the result of the need for a portable, consistent, flexible and DRY attachment system in a project I'm currently working on. As Django provides an excellent base for this with the `ContentTypes framework`_, and provides a great example for how to implement this in their `Comments framework`_, this proved to be an (almost) trivial task.


Features
--------

* Based on the `Comments framework`_, which means it should be quite recognizable.
* Seamless integration with the existing FileSystemStorage backend
* Database storage bacends. This allows you to store files directly in the database. No manual configuration or creation of database tables are required (Only PostgreSQL and SQLite implemented so far).
* No unit tests whatsoever! This is completly untested code, no kidding!

.. todo::
    Write a unit test suite, and make it pass!

.. warning::
    Storing files in your database should be used with caution if you have lots of attachments. This might severly degrade your database performance. Storing files in your filesystem (after all, that's what filesystems do best) are much more efficient performance wise.


Want to help?
-------------

As I don't have access to either a MySQL (yes, I could just install it) or an Oracle database, nor do I have any skills on either databases, database backend support on these needs to be implemented.

If you want to help out, fork `django-files`_ on github, implement the backend, and submit a pull request!

Bug fixes are of course also welcome =)

.. _ContentTypes framework: https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/
.. _Comments framework: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
.. _django-files: https://github.com/rhblind/django-files

