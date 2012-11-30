===============
Admin interface
===============

As you probably know, Django comes with a nice `admin interface`_.
The django-files app comes with two pre-configured classes for using in the admin interface; A `ModelAdmin`_ class for the Attachment model, and a pretty basic `GenericStackedInline`_ class you can use to hook into your models which has files attached.


AttachmentAdmin
===============

:class:`files.admin.AttachmentAdmin`

By enabling the admin `autodiscover`_ feature, this should automatically appear in your admin site.


AttachmentInlines
=================

:class:`files.admin.AttachmentInlines`

This generic inline can be used to get a nice list of attachments related to some object.
Take our Shape model from previous examples.

.. code-block:: python
    
    from django.contrib import admin
    from demosite.models import Shape
    from files.admin import AttachmentInlines

    class ShapeAdmin(admin.ModelAdmin):
        inlines = [AttachmentInlines]

        def save_formset(self, request, form, formset, change):
            instances = formset.save(commit=False)
            for obj in instances:
                # Always save IP address of changed objects
                obj.ip_address = request.META["REMOTE_ADDR"]
                obj.save()
            formset.save_m2m()
        
                   
    admin.site.register(Shape, ShapeAdmin)


Permissions
===========

The user in question needs to be a `staff`_ member to be able to log into the `admin interface`_.

In addition, the following conditions must be met.

* Add a new attachment 
    * The loggin in user needs to have the `files.add_attachment` permission.
* Delete
    * The logged in user needs to have `superuser`_ status.
* Change
    * The loggine in user needs to have `files.change_attachment` permission. 





.. _admin interface: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#modeladmin-objects
.. _autodiscover: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
.. _ModelAdmin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#modeladmin-objects
.. _GenericStackedInline: https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/#generic-relations-in-forms-and-admin
.. _superuser: https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User.is_superuser
.. _staff: https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.models.User.is_staff
