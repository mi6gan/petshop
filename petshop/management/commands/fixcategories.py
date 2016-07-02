from django.core.management.base import BaseCommand
from django.utils import translation

from oscar.core.loading import get_model


class Command(BaseCommand):

    def handle(self, verbosity, *args, **kwargs):
        Category = get_model('catalogue', 'Category')
        Category.fix_tree()
