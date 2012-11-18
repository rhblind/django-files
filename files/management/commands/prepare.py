# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    """
    Create database table for the database attachment backend
    if required
    """
    def handle_noargs(self, **options):
        pass
