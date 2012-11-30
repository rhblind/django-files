# -*- coding: utf-8 -*-

import time
from django import forms
from django.conf import settings
from django.forms.util import ErrorDict
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.translation import ugettext_lazy as _

from files.models import Attachment
from django.contrib.contenttypes.models import ContentType


class AttachmentForm(forms.ModelForm):
    """
    Modelform for uploading and/or editing
    attachments.
    """
    # Security fields
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)
    honeypot = forms.CharField(required=False, label=_("If you enter anything in this field "\
                                                       "your attachment fill be treated as spam."))

    def __init__(self, target_object, *args, **kwargs):
        self.target_object = target_object
        initial = kwargs.pop("initial", {})
        initial.update(self.generate_security_data())
        kwargs["initial"] = initial
        super(AttachmentForm, self).__init__(*args, **kwargs)
        self.fields["description"].widget.attrs["placeholder"] = "File description"
    
    class Meta:
        model = Attachment
        fields = ("content_type", "object_id", "description", "attachment",
                  "is_public", "timestamp", "security_hash", "honeypot")
        widgets = {
            "content_type": forms.HiddenInput(),
            "object_id": forms.HiddenInput(),
        }
    
    def security_errors(self):
        """
        Return the errors associated with security.
        """
        errors = ErrorDict()
        for f in ["honeypot", "timestamp", "security_hash"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors
    
    def generate_security_data(self):
        """
        Generate initial security data for the form.
        """
        timestamp = int(time.time())
        security_dict = {
            "content_type": ContentType.objects.get_for_model(self.target_object),
            "object_id": str(self.target_object._get_pk_val()),
            "timestamp": str(timestamp),
            "security_hash": self.initial_security_hash(timestamp)
        }
        return security_dict
    
    def initial_security_hash(self, timestamp):
        """
        Get the initial security hash from self.content_object
        and a (unix) timestamp.
        """
        initial_security_dict = {
            "content_type": ContentType.objects.get_for_model(self.target_object),
            "object_id": str(self.target_object._get_pk_val()),
            "timestamp": str(timestamp)
        }
        return self.generate_security_hash(**initial_security_dict)
        
    def generate_security_hash(self, content_type, object_id, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        ctype = u".".join((content_type.app_label, content_type.model))
        info = (ctype, object_id, timestamp)
        key_salt = "files.forms.AttachmentForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()
    
    def clean_security_hash(self):
        """
        Make sure the security hash match what's expected.
        """
        try:
            security_hash_dict = {
                "content_type": ContentType.objects.get_for_id(self.data["content_type"]),
                "object_id": self.data["object_id"],
                "timestamp": self.data["timestamp"]
            }
            
            expected = self.generate_security_hash(**security_hash_dict)
            actual = self.cleaned_data["security_hash"]
            if not constant_time_compare(expected, actual):
                raise
        except Exception:
            raise forms.ValidationError("Security hash dict failed.")
        return actual
    
    def clean_attachment(self):
        """
        Make sure the attachment file size is allowed.
        """
        attachment = self.cleaned_data["attachment"]
        max_size = getattr(settings, "ATTACHMENT_MAX_SIZE", None)
        if max_size and attachment.size > max_size:
            raise forms.ValidationError(_("File is too large! " \
                  "Please keep attachment size under %d bytes." % max_size))
        return attachment
        
    def clean_timestamp(self):
        """
        Make sure the timestamp is not too far (> 2 hours) in the past.
        """
        timestamp = self.cleaned_data["timestamp"]
        if time.time() - timestamp > (2 * 60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return timestamp
    
    def clean_honeypot(self):
        """
        Make sure the honeypot field is empty.
        """
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value
