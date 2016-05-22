from django.core.management.base import BaseCommand

from oscar.core.loading import get_model


class Command(BaseCommand):

    def handle(self, verbosity, *args, **kwargs):
        Product = get_model('catalogue', 'Product')
        StockRecord = get_model('partner', 'StockRecord')
        invalid = Product.objects.filter(
                structure=Product.PARENT, stockrecords__isnull=False)
        count = invalid.count()
        if count:
            if verbosity > 2:
                self.stdout.write('found %s parent products'
                                  ' with stock records'
                                  ', deleting records' % count)
            StockRecord.objects.filter(product__in=invalid).delete()
        elif verbosity > 2:
            self.stdout.write('products are valid')
