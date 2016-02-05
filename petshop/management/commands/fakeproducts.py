from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from oscar.core.loading import get_model
from oscar.core.utils import slugify

import random

from petshop.core.commands import FakeModelCommand


class Command(FakeModelCommand):
    model = get_model('catalogue', 'Product')
    default_count = 100
    bulk = False

    def handle(self, *args, **kwargs):
        ProductClass = get_model('catalogue', 'ProductClass')
        self.product_class = ProductClass.objects.get_or_create(
                **settings.DEFAULT_PRODUCT_CLASS)[0]
        Partner = get_model('partner', 'Partner')
        self.partner = Partner.objects.get_or_create(
                **settings.DEFAULT_PARTNER)[0]
        return super(Command, self).handle(*args, **kwargs)

    def get_model_kwargs(self, fake, default_fake, i):
        title = u' '.join(fake.words(nb=random.randrange(1, 5)))
        kwargs = dict(
            title=title,
            upc=default_fake.ean8(),
            description=fake.text(max_nb_chars=500),
            slug=slugify(title),
            product_class=self.product_class
        )
        return kwargs

    def postprocess_objects(self, objects, fake, default_fake):
        StockRecord = get_model('partner', 'StockRecord')
        Category = get_model('catalogue', 'Category')
        ProductCategory = get_model('catalogue', 'ProductCategory')
        product_categories = []
        for product in objects:
            StockRecord.objects.update_or_create(
                    product=product, partner=self.partner,
                    defaults=(
                        dict(partner_sku=u'%s_%s' % (
                            product.upc, default_fake.ean8()),
                            num_in_stock=100,
                            price_excl_tax=random.randrange(10, 10000))))
            if not product.categories.exists():
                category = Category.objects.filter(
                        numchild=0).order_by('?').first()
                if category:
                    product_categories.append(ProductCategory(
                                category=category, product=product))
        ProductCategory.objects.bulk_create(product_categories)
