# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from django.db.transaction import commit_on_success
from demosite.models import Shape


class Command(NoArgsCommand):
    """
    Initialize some test data
    """

    @commit_on_success
    def handle_noargs(self, **options):

        shape = Shape.objects.create(**{
            "color": "green",
            "shape": "square",
            "descr": "A green square"
        })
        if shape.pk:
            self.stdout.write("Created Green Square test object.\n")
        else:
            self.stdout.write("Could not create test object.")
