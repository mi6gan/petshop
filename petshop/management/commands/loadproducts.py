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
                    '--rows', type=int, nargs='+',
                    help='row numbers to parse from the source table')
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
        row_ns = kwargs.get('rows')
        Product = get_model('catalogue', 'Product')
        if clear:
            Category = get_model('catalogue', 'Category')
            Category._base_manager.all().delete()
            Product.objects.all().delete()
        data_file = kwargs.get('data_file', False)
        if data_file: 
            for instance in load_products_from_csv(data_file, row_ns):
                self._model_message(instance, False, verbosity)
                if getattr(instance, 'parent', False):
                    self.stdout.write(
                            'product is child of %s' % force_text(
                                str(instance.parent)))
                else:
                    self.stdout.write('product is standalone')
                self.stdout.write('\n')
