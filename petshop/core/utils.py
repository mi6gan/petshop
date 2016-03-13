from decimal import Decimal as D
from django.conf import settings

from oscar.core.loading import get_model
from oscar.core.utils import slugify

import unicodecsv as csv


def load_products_from_csv(data_file):
    if hasattr(data_file, 'open'):
        data_file.open('r')
    Category = get_model('catalogue', 'Category')
    Product = get_model('catalogue', 'Product')
    ProductCategory = get_model('catalogue', 'ProductCategory')
    ProductClass = get_model('catalogue', 'ProductClass')
    ProductAttribute = get_model('catalogue', 'ProductAttribute')
    ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
    Partner= get_model('partner', 'Partner')
    StockRecord = get_model('partner', 'StockRecord')
    reader = csv.reader(data_file)
    header = None
    product_class = (ProductClass.objects.get_or_create(
        **settings.DEFAULT_PRODUCT_CLASS))[0]
    parsed_parents = []
    parsed_attributevalues = []
    product = None
    for row in list(reader) + [None]:
        if not header:
            header = [c.strip() for c in row]
        elif row:
            (upc, title, partner_sku, partner_code, partner_price,
             price, main_category, categories, desc) = (
                    c.strip() for c in row[0:9])
            title = title
            slug = slugify(u'%s_%s' % (title, upc))
            upc = '%s%s' % ('0'*(10-len(str(upc))), upc)
            product = Product.objects.filter(upc=upc).first()
            child = None
            if product and product in parsed_parents:
                for child in product.children.all():
                    for attribute, value in parsed_attributevalues:
                        product_attribute = None
                        for product_attribute in (
                                ProductAttributeValue.objects.filter(
                                        product=product, attribute=attribute)):
                            if product_attribute.value == value:
                                product_attribute = None
                                break
                        if not product_attribute:
                            child = None
                    if child:
                        product = child
                        break
                if not child:
                    product.structure = Product.PARENT
                    product.save()
                    child = Product.objects.create(
                            parent=product, structure=Product.CHILD)
                    product = child
            else:
                product, __ = Product.objects.update_or_create(
                    upc=upc, defaults={
                        'title': title,
                        'slug': slug,
                        'product_class': product_class})
            partner, __ = Partner.objects.update_or_create(
                    code=partner_code, defaults={'name': partner_code})
            if not partner_sku:
                partner_sku = '%s_%s_%s' % (
                        partner_code, upc, partner.stockrecords.count())
            stockrecord, __ = StockRecord.objects.get_or_create(
                        product=product, partner=partner,
                        defaults={
                            'partner_sku': partner_sku,
                            'num_in_stock': 100000,
                            'price_excl_tax': D(price.replace(',', '.'))})
        if product:
            yield product
            for attribute, value in parsed_attributevalues:
                attribute.save_value(product, value)
            parsed_attributevalues = []
        if row:
            for i, attribute_or_value in enumerate(row[9:]):
                if i % 2 is 0:
                    attribute_name = attribute_or_value
                    attribute_code = slugify(attribute_name)
                    attribute, created = (
                            ProductAttribute.objects.update_or_create(
                        code=attribute_code,
                        defaults={'name': attribute_name},
                        type=ProductAttribute.TEXT))
                else:
                    value = attribute_or_value
                    parsed_attributevalues.append((attribute, value))
        if product and product.structure is not Product.CHILD:
            categories = tuple(main_category.split('\\'))
            parent_category = None
            category = None
            for i, category_name in enumerate(categories):
                name = category_name.strip().capitalize()
                slug = slugify(category_name)
                category = Category.objects.filter(slug=slug).first()
                if not category:
                    if not parent_category:
                        category = Category.add_root(name=name, slug=slug)
                    else:
                        category = parent_category.add_child(
                                name=name, slug=slug)
                parent_category = category
            if category:
                ProductCategory.objects.get_or_create(
                        product=product, category=category)
            parsed_parents.append(product)
