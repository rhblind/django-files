# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from django.db.transaction import commit_on_success


class Command(NoArgsCommand):
    """
    Initialize some data for the demosite
    """
    
    @commit_on_success
    def handle_noargs(self, **options):
        pass
