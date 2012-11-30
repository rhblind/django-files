# -*- coding: utf-8 -*-
#
# This is an implementation of the django.contrib.comments
# framework template tags adapted to use with attachments.
#

from __future__ import absolute_import

import files

from django import template
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import get_storage_class

register = template.Library()


class BaseAttachmentNode(template.Node):
    """
    Base helper class for handling the get_attachment_* template
    tags.
    Modelled after the contrib.comments framework
    """
    
    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse get_attachment_list/count/form
        and return a Node
        """
        tokens = token.contents.split()
        if tokens[1] != "for":
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])
        
        # {% get_whatever for obj as varname %}
        if len(tokens) == 5:
            if tokens[3] != "as":
                raise template.TemplateSyntaxError("Third argument in %r must be 'as'" % tokens[0])
            return cls(object_expr=parser.compile_filter(tokens[2]),
                       as_varname=tokens[4])
        elif len(tokens) == 6:
            if tokens[4] != "as":
                raise template.TemplateSyntaxError("Fourth argument in %r must be 'as'" % tokens[0])
            return cls(ctype=BaseAttachmentNode.lookup_content_type(tokens[2], tokens[0]),
                       object_pk_expr=parser.compile_filter(tokens[3]),
                       as_varname=tokens[5])
        else:
            raise template.TemplateSyntaxError("%r tag requires 4 or 5 arguments" % tokens[0])

    @staticmethod
    def lookup_content_type(token, tagname):
        try:
            app, model = token.split(".")
            return ContentType.objects.get_by_natural_key(app, model)
        except ValueError:
            raise template.TemplateSyntaxError("Third argument in %r must be in the formate 'app.model'" % tagname)
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError("%r tag has non-existant content-type: '%s.%s'" % (tagname, app, model))
        
    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None, as_varname=None, attachment=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError("Attachment nodes must be given either a literal object or a ctype and object pk.")
        
        self.attachment_model = files.get_model()
        self.as_varname = as_varname
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr
        self.attachment = attachment
        
    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ""
    
    def get_query_set(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return  self.attachment_model.objects.none()
        
        qs = self.attachment_model.objects.filter(
                content_type=ctype,
                object_id=smart_unicode(object_pk),
                site__pk=settings.SITE_ID)
        
        # The 'is_public' field and the 'backend' fields are implementation
        # details of the 'django-files' app. If present on the attachment
        # model, filter on them.
        field_names = [f.name for f in self.attachment_model._meta.fields]
        if "is_public" in field_names:
            qs = qs.filter(is_public=True)
        if "backend" in field_names:
            engine = str(get_storage_class().__name__)
            qs = qs.filter(backend=engine)
        
        return qs
    
    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_pk_expr.resolve(context, ignore_failures=True)
        
    def get_context_value_from_queryset(self, context, qs):
        """
        Subclasses should override this.
        """
        raise NotImplementedError
    
    
class AttachmentListNode(BaseAttachmentNode):
    """
    Insert a list of attachments into the context
    """
    def get_context_value_from_queryset(self, context, qs):
        return list(qs)


class AttachmentCountNode(BaseAttachmentNode):
    """
    Insert a count of attachments into the context
    """
    def get_context_value_from_queryset(self, context, qs):
        return qs.count()


class AttachmentFormNode(BaseAttachmentNode):
    """
    Insert a form for the attachment model into the context
    """
    
    def get_form(self, context):
        obj = self.get_object(context)
        if obj:
            return files.get_form()(obj)
        else:
            return None
        
    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None
        else:
            object_pk = self.object_pk_expr.resolve(context, ignore_failures=True)
            return self.ctype.get_object_for_this_type(pk=object_pk)
        
    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ""
    

class AttachmentEditFormNode(AttachmentFormNode):
    """
    Insert a form for the attachment model instance into the context
    """
       
    def get_form(self, context):
        obj = self.get_object(context)
        if obj:
            target_obj = obj.content_type.get_object_for_this_type(pk=obj.object_id)
            return files.get_form()(target_obj, **{"instance": obj})
        else:
            return None
    

class RenderAttachmentFormNode(AttachmentFormNode):
    """
    Render the attachment form directly
    """
    
    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse render_comment_form and return a Node.
        """
        tokens = token.contents.split()
        if tokens[1] != "for":
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_attachment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_attachment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseAttachmentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "attachments/%s/%s/form.html" % (ctype.app_label, ctype.model),
                "attachments/%s/form.html" % ctype.app_label,
                "attachments/%s/form.html" % ctype.model,
                "attachments/form.html"
            ]
            context.push()
            formstr = render_to_string(template_search_list, {"form": self.get_form(context)}, context)
            context.pop()
            return formstr
        else:
            return ""


class RenderAttachmentEditFormNode(RenderAttachmentFormNode, AttachmentEditFormNode):
    """
    Render the edit form directly
    """
    
    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "attachments/%s/%s/edit_form.html" % (ctype.app_label, ctype.model),
                "attachments/%s/edit_form.html" % ctype.app_label,
                "attachments/%s/edit_form.html" % ctype.model,
                "attachments/edit_form.html"
            ]
            context.push()
            formstr = render_to_string(template_search_list, {"form": self.get_form(context)}, context)
            context.pop()
            return formstr
        else:
            return ""


class RenderAttachmentListNode(AttachmentListNode):
    """
    Render the attachment list directly
    """

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse render_attachment_list and return a Node.
        """
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_list for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_comment_list for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseAttachmentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            template_search_list = [
                "attachments/%s/%s/list.html" % (ctype.app_label, ctype.model),
                "attachments/%s/list.html" % ctype.app_label,
                "attachments/%s/list.html" % ctype.model,
                "attachments/list.html"
            ]
            qs = self.get_query_set(context)
            context.push()
            liststr = render_to_string(template_search_list, {
                "attachment_list": self.get_context_value_from_queryset(context, qs)
            }, context)
            context.pop()
            return liststr
        else:
            return ""


@register.tag
def render_attachment_list(parser, token):
    """
    Render the attachment list (as returned by ``{% get_attachment_list %}``)
    through the ``attachments/list.html`` template

    Syntax::

        {% render_attachment_list for [object] %}
        {% render_attachment_list for [app].[model] [object_id] %}

    Example usage::

        {% render_attachment_list for event %}

    """
    return RenderAttachmentListNode.handle_token(parser, token)


@register.tag
def render_attachment_form(parser, token):
    """
    Render the attachment form (as returned by ``{% render_attachment_form %}``) through
    the ``attachments/form.html`` template.

    Syntax::

        {% render_attachment_form for [object] %}
        {% render_attachment_form for [app].[model] [object_id] %}
    """
    return RenderAttachmentFormNode.handle_token(parser, token)


@register.tag
def render_attachment_editform(parser, token):
    """
    Render the attachment form (as returned by ``{% render_attachment_editform %}``) through
    the ``attachments/editform.html`` template.

    Syntax::

        {% render_attachment_editform for [object] %}
        {% render_attachment_editform for [app].[model] [object_id] %}
    """
    return RenderAttachmentEditFormNode.handle_token(parser, token)


@register.tag
def get_attachment_form(parser, token):
    """
    Get a (new) form object to upload a new attachment.

    Example usage::

        {% get_attachment_form for [object] as [varname] %}
        {% get_attachment_form for [app].[model] [object_id] as [varname] %}
    """
    return AttachmentFormNode.handle_token(parser, token)


@register.tag
def get_attachment_editform(parser, token):
    """
    Get a modelform object to edit an existing attachment.

    Syntax::

        {% get_attachment_editform for [object] as [varname] %}
        {% get_attachment_editform for [app].[model] [object_id] as [varname] %}
    """
    return AttachmentEditFormNode.handle_token(parser, token)


@register.tag
def get_attachment_count(parser, token):
    """
    Gets the attachment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_attachment_count for [object] as [varname]  %}
        {% get_attachment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_attachment_count for event as comment_count %}
        {% get_attachment_count for calendar.event event.id as comment_count %}
        {% get_attachment_count for calendar.event 17 as comment_count %}

    """
    return AttachmentCountNode.handle_token(parser, token)


@register.tag
def get_attachment_list(parser, token):
    """
    Gets the list of attachments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_attachment_list for [object] as [varname]  %}
        {% get_attachment_list for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_attachment_list for event as attachment_list %}
        {% for attachment in attachment_list %}
            ...
        {% endfor %}

    """
    return AttachmentListNode.handle_token(parser, token)


@register.simple_tag
def get_create_target():
    """
    Get the target URL for the attachment form.

    Example::

        <form action="{% get_create_target %}" method="post">
    """
    return files.get_create_target()


@register.simple_tag
def get_edit_target(attachment):
    """
    Get the edit URL for an attachment.

    Example::

        <a href="{% get_edit_target attachment %}">edit</a>
    """
    # This is just a helper method which calls the
    # get_edit_url for the attachment.
    return files.get_edit_url(attachment)


@register.simple_tag
def get_view_url(attachment):
    """
    Get the view URL for an attachment.

    Example::
        
        <a href="{% get_view_url attachment %}">view</a>
    """
    return files.get_view_url(attachment)


@register.simple_tag
def get_edit_url(attachment):
    """
    Get the edit URL for an attachment.

    Example::

        <a href="{% get_edit_url attachment %}">edit</a>
    """
    return files.get_edit_url(attachment)


@register.simple_tag
def get_delete_url(attachment):
    """
    Get the delete URL for an attachment.

    Example::
        
        <a href="{% get_delete_url attachment %}">delete</a>
    """
    return files.get_delete_url(attachment)


@register.simple_tag
def get_download_url(attachment):
    """
    Get the download URL for an attachment.

    Example::
        
        <a href="{% get_download_url attachment %}">download</a>
    """
    return files.get_download_url(attachment)
