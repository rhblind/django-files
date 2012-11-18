# -*- coding: utf-8 -*-

from django.dispatch import Signal

write_binary = Signal(providing_args=["instance", "content", "kwargs"])
unlink_binary = Signal(providing_args=["instance", "kwargs"])
