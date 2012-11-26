# -*- coding: utf-8 -*-
#
# Signals related to attachments
#

from django.dispatch import Signal

# Sent after the attachment has been saved to the database if using
# one of the database backends. This signals calls the write_binary
# method in the respective storage backend configured in settings.py
# and updates the provided instance database row with the binary
# data of the attachment.
write_binary = Signal(providing_args=["instance", "content", "kwargs"])

# Sent after binary data has been saved to the database.
post_write = Signal(providing_args=["instance", "kwargs"])

# Sent just before the attachment will be deleted from the database.
# This signal calls the unlink_binary method of the storage backend
# if existing, which will properly perform neccesary steps to
# safely remove the binary data from the database (if required).
unlink_binary = Signal(providing_args=["instance", "kwargs"])

# Sent after the unlinking is done. Note that this signal is sent
# even if the storage backend does not requires any unlinking.
post_unlink = Signal(providing_args=["instance", "kwargs"])
