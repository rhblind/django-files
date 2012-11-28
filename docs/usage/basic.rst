Basic usage
===========

If you have downloaded the git version, you will see that it includes a demosite app, which demonstrates the use of django-files. In the demosite we have a model called `Shape` which we will use through this documentation as the object we relate our attachments to.


The `demosite/models.py` file

.. literalinclude:: ../../demosite/models.py


Let's assume we create a row in our database like this

.. code-block:: python
    
    >>> from demosite.models import Shape
    >>> s = Shape(shape="square", color="green", descr="A green square")
    >>> s.save()
    >>> Shape.objects.all()
    [<Shape: green square>]


We now have a `green square` object which we can add some attachments to.

Hooking into the attachments framework
--------------------------------------

If you have ever used the `Comments framework`_ in Django, this should be quite familiar. The django-files app comes with a number of template tags which are used to manage the attachments related to objects.


.. note::
    Remember to load the attachment template tags into your context like this.

    .. code-block:: html+django

        {% load attachments %}


Say we have a view rendering a template with a `shapes` queryset in the context.


Adding attachments
------------------

:py:meth:`files.templatetags.attachments.render_attachment_form`

.. code-block:: html+django

    <h1>Render the upload form</h1>

    {% load attachments %}

    <div>
        {% for shape in shapes %}

            {% render_attachment_form for shape %}
        
        {% endfor %}
    </div>

As in the `Comments framework`_ this will render a upload form directly into the context.
Or, alternatively, if you wish to render your form fields independently:

:py:meth:`files.templatetags.attachments.get_attachment_form`


.. code-block:: html+django
        
    {% get_attachment_form for shape as form %}

    <form action="{% attachment_form_target %}" method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {% for field in form %}
            
            {{ field }}

        {% endfor %}

        <input type="submit" name="submit" value="{% trans "Upload file" %}" />
    </form>


In which case you will need to provide the rest of the `<form>` as well as 
`<submit />` buttons yourself.

.. tip::
    :py:meth:`~files.templatetags.attachments.attachment_form_target` can be used to retrieve the
    url for the view which should accept the POST request.

The form template will search a number of location for a template, and return the first that match, so that you can easily override the default template.

|more| See :ref:`templates` for more info how to customize your templates.


Editing attachments
-------------------

The edit form works in the same manners as the create form, with both a method for rendering the form directly into the context, or to store the form in a context variable and manually render the individual fields of the form.

:py:meth:`files.templatetags.attachments.render_attachment_editform`

.. code-block:: html+django

    <h1>Render the edit form</h1>

    {% load attachments %}

    <div>
        {% for shape in shapes %}

            {% render_attachment_editform for shape %}
        
        {% endfor %}
    </div>


:py:meth:`files.templatetags.attachments.get_attachment_editform`

.. code-block:: html+django
        
    {% get_attachment_editform for shape as form %}

    <form action="{{ attachment_edit_url }}" method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {% for field in form %}
            
            {{ field }}

        {% endfor %}

        <input type="submit" name="submit" value="{% trans "Save changes" %}" />
    </form>

.. attention::
    When editing an existing attachment, a special variable `{{ attachment_edit_url }}` will be
    inserted into the context dictionary in the template tag's render() method.

Listing attachments
-------------------

Similary we can render a list of attachments related to an object by using the

:py:meth:`files.templatetags.attachments.render_attachment_list`

.. code-block:: html+django

    {% render_attachment_list for shape %}

Or get the list as a context variable

:py:meth:`files.templatetags.attachments.get_attachment_list`

.. code-block:: html+django

    {% get_attachment_list for shape as attachment_list %}

    {% for item in attachment_list %}

        {{ item }}

    {% endfor %}


.. _Comments framework: https://docs.djangoproject.com/en/dev/ref/contrib/comments/

.. |more| image:: ../images/info.png
    :align: middle
    :alt: more info
