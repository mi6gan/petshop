from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation
from django.utils.encoding import force_text

from oscar.core.loading import get_model

from petshop.core.utils import load_products_from_csv


class Command(BaseCommand):

    def add_arguments(self, parser):
            parser.add_argument(
                    'data_file', type=open, help='path to csv file')
            parser.add_argument(
                    '--clear', action='store_true',
                    help='clear exist data')


    def _model_message(self, instance, created, verbosity, level=0):
        if verbosity < 3:
            return
        message = u'{0}{1} {2} "{3}"'.format(
            '\t'*level,
            'Adding' if created else 'Updating',
            type(instance)._meta.model_name,
            force_text(str(instance)))
        self.stdout.write(message)

    def handle(self, verbosity, *args, **kwargs):
        clear = kwargs.get('clear', False)
        photos = kwargs.get('photos', False)
        if clear:
            Category = get_model('catalogue', 'Category')
            Product = get_model('catalogue', 'Product')
            Category.objects.all().delete()
            Product.objects.all().delete()
        data_file = kwargs.get('data_file', False)
        if data_file: 
            for instance in load_products_from_csv(data_file):
                self._model_message(instance, False, verbosity)
