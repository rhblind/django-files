.. _templates:

==========================
Override default templates
==========================

If you wish to override the default templates (you probably will), this is how to do it.


The following paths are being used by the template tags and views

The search path is as follows (in this order):

    #. "attachments/`app_label`/`model`/`<template name>`.html"
    #. "attachments/`app_label`/`<template name>`.html"
    #. "attachments/`model`/`<template name>`.html"
    #. "attachments/`<template name>`.html"

where app_label is the `app_label` of the model which the attachment should be related to (in our case `demosite`), and the model is the `model` which the attachment should be related to (in our case `shape`).

This means that you can create a different form (if you choose to) for

* Each of your models (in one or more) of your apps
* A form for all your models in one or more apps
* One form for all your models across your entire project that shares a name
* Or just use a single form for your entire project


form.html
---------

Used by:
    * :class:`files.views.AttachmentCreateView`
    * :py:meth:`files.templatetags.attachments.render_attachment_form`
    * :py:meth:`files.templatetags.attachments.get_attachment_form`

Template used to render an upload form when adding a new attachment to some object.


edit_form.html
--------------

Used by:
    * :class:`files.views.AttachmentEditView`
    * :py:meth:`files.templatetags.attachments.render_attachment_editform`
    * :py:meth:`files.templatetags.attachments.get_attachment_editform`

Template used to render an edit form for an existing attachment.


list.html
---------

Used by:
    * :py:meth:`files.templatetags.attachments.render_attachment_list`
    * :py:meth:`files.templatetags.attachments.get_attachment_list`

Render a list of attachments.


view.html
---------

Used by:
    * :class:`files.views.AttachmentDetailView`

Template for viewing the details of the attachment.


delete.html
-----------

Used by:
    * :class:`files.views.AttachmentDeleteView`

Template used to show the "Really delete this attachment?", and eventually post to the DeleteAttachmentView which performs the delete action.


deleted.html
------------

Used by:
    * :class:`files.views.AttachmentDeleteView`

After deleting an attachment, redirects to this template unless a `next` value is provided.


400-debug.html
--------------

A standard 400 error page used if settings.DEBUG = True
Not used in production mode.
