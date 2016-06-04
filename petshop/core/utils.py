from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site 
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.template.context import RequestContext
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_string
from django.utils import timezone

from oscar.core.loading import get_model
from oscar.core.utils import slugify

import json
import logging
import os
import random
import requests
import unicodecsv as csv
from hashlib import md5
from decimal import Decimal as D
import easywebdav
from bs4 import BeautifulSoup as bs
from PIL import Image
from io import BytesIO
from urllib import quote, unquote


def yandex_money_checksum(**kwargs):
    check_str = ';'.join(str(kwargs.get(k, '')) for k in (
        'action', 'orderSumAmount', 'orderSumCurrencyPaycash',
        'orderSumBankPaycash', 'shopId', 'invoiceId', 'customerNumber',
        'shopPassword'))
    checksum = md5(check_str).hexdigest().upper()
    return checksum

def send_email_to(request, commtype_code, ctx, rcpnts):
    if not 'site' in ctx:
        site=get_current_site(request)
        ctx.update(site=site)
    CommunicationEventType = get_model("customer", "CommunicationEventType")
    try:
        event_type = CommunicationEventType.objects.get(
                    code=commtype_code)
    except CommunicationEventType.DoesNotExist:
        messages = CommunicationEventType.objects.get_and_render(
                    commtype_code, ctx)
    else:
        messages = event_type.get_messages(ctx)
        rcpnts = set(rcpnts)
        rcpnts.update(staff.email for staff in event_type.staff.all())
    send_mail(messages.get('subject'), messages.get('body'),
              settings.SERVER_EMAIL, list(rcpnts),
              html_message=messages.get('html'))


def send_email_to_managers(request, commtype_code, ctx):
    site = get_current_site(request)
    ctx.update({'site': site})
    managers_emails = set(m[1] for m in settings.MANAGERS)
    send_email_to(request, commtype_code, ctx, managers_emails)

def send_email_to_admins(request, commtype_code, ctx):
    site = get_current_site(request)
    ctx.update({'site': site})
    admins_emails = set(a[1] for a in settings.ADMINS)
    send_email_to(request, commtype_code, ctx, admins_emails)

def process_image_file(image_file, image_width): 
    try:
        pil_image = Image.open(image_file)
    except IOError:
        pass
    else:
        size = (image_width, (
            image_width*pil_image.size[1])/pil_image.size[0])
        if (size[0] >= pil_image.size[0]) or (size[1] >= pil_image.size[1]):
            pil_image = pil_image.resize(size, Image.BICUBIC)
            image_file = BytesIO()
            pil_image.save(image_file, format='JPEG')
        image_file.seek(0)
        return image_file

def load_products_photos(root_path, image_width, clear):
    Product = get_model('catalogue', 'Product')
    ProductImage = get_model('catalogue', 'ProductImage')
    StockRecord = get_model('partner', 'StockRecord')
    Partner = get_model('partner', 'Partner')
    webdav = easywebdav.connect(
        settings.WEBDAV_HOST,
        username=settings.WEBDAV_USERNAME,
        password=settings.WEBDAV_PASSWORD,
        protocol=settings.WEBDAV_PROTOCOL)
    parsed_products = set()
    next_paths = [easywebdav.client.File(quote(root_path), 0, None, None, '')]
    paths_for_partner = {}

    yield 'Walking through file paths tree', ''
    yield '-'*40, 'INFO'
    image_paths = []
    images = []
    while next_paths:
        paths = list(next_paths)
        next_paths = []
        dirname_to_partner_code = {}
        for path in paths:
            yield ('parsing "%s"' % unquote(path.name)), 'INFO'
            if path.name.endswith('/'):
                cur_paths = webdav.ls(path.name)
                if not cur_paths:
                    yield ('\tis empty dir, skipping'), 'NOTICE'
                else:
                    next_paths += filter(
                            lambda p: p.name != path.name, cur_paths)
            elif path.contenttype.startswith('image/'):
                image_paths.append(path)
                yield ('\tis image, adding to image paths'), 'INFO'
            else:
                yield ('\t unrecognized content'
                       ' type "%s", skipping' % path.contenttype), 'NOTICE'

    yield '\nfound %s image files to load' % len(image_paths), ''
    yield '-'*40, 'INFO'
    for path in image_paths:
        yield ('trying to load "%s"' % unquote(path.name)), 'INFO'
        dirname = os.path.dirname(path.name)
        partner_code = dirname_to_partner_code.get(dirname, False)
        if not partner_code:
            for part in dirname.split('/'):
                code = slugify(part)
                if Partner.objects.filter(
                    code__iexact=code).exists():
                        dirname_to_partner_code[dirname] = code
                        partner_code = code
                        break
        if not partner_code:
            yield ('\tno valid partner for image in path, skipping'), 'ERROR'
            continue
        sku = os.path.basename(path.name).split('.')[0].strip()
        sku = slugify(sku)
        srecord = StockRecord.objects.filter(
            partner_sku__iregex=(r'^0*%s$' % sku.lstrip('0')),
            partner__code__iexact=partner_code).first()
        if srecord:
            image_file = BytesIO()
            webdav.download(path.name, image_file)
            image_file.seek(0)
            product = srecord.product
            product_images = ProductImage.objects.filter(product=product)
            if not clear and product_images.exists():
                yield ('\tskipping, image already exists', 'NOTICE')
                continue
            if clear and product not in parsed_products:
                for product_image in ProductImage.objects.filter(
                        product=product):
                    product_image.original.delete()
                    product_image.delete()
            else:
                parsed_products.add(product)
            image_file = process_image_file(image_file, image_width)
            if not image_file:
                yield ('\tskipping, corrupt image file', 'NOTICE')
            else:
                image=ProductImage.objects.get_or_create(
                            product=product, display_order = 0)[0]
                image.original.save(path.name.split('/')[-1],
                                    ContentFile(image_file.read()))
                image.save()
                images.append(image)
                yield ('\tattached image "%s" to "%s"' % (
                    unquote(os.path.basename(path.name)),
                    product)), 'SUCCESS'
        else:
                yield ('\tproduct with sku "%s" for partner'
                       ' "%s" is not found' % (
                           sku, partner_code)), 'ERROR'
        yield '\n', 'INFO'
    yield 'uploaded %s product images' % len(images), ''

def load_petline_photos(image_width, clear):
    URL_BASE = "http://www.petline.ru"
    SEARCH_URL_PATTERN = "%s/search/?text=%s"
    Partner = get_model('partner', 'Partner')
    ProductImage = get_model('catalogue', 'ProductImage')
    partner = Partner.objects.filter(code="petline").first()
    images = []
    if not partner:
        yield 'partner with code petline is not found', 'ERROR'
    else:
        for srecord in partner.stockrecords.all():
            product = srecord.product
            sku = srecord.partner_sku.lstrip('0')
            yield 'trying to find image for sku %s' % sku, 'INFO'
            response = requests.get(SEARCH_URL_PATTERN % (URL_BASE, sku))
            results = bs(response.content, 'html5lib')
            link = results.select_one('.shop_items li.item .over .pic a')
            href = link.get('href') if link else None
            if href:
                response = requests.get(''.join([URL_BASE, href]))
                item = bs(response.content, 'html5lib')
                for img_link in item.select(
                        '.shop_item .pics'
                        ' .connected-carousels .pic a'):
                    href = img_link.get('href')
                    if href:
                        yield 'found image at %s' % href, 'INFO'
                        response = requests.get(''.join([URL_BASE, href]))
                        image_file = BytesIO(response.content)
                        image_file.seek(0)
                        image_file = process_image_file(image_file, image_width)
                        if not image_file:
                            yield ('\tskipping, corrupt image file', 'NOTICE')
                        else:
                            images_count = ProductImage.objects.filter(
                                    product=product).count()
                            image, __ = ProductImage.objects.get_or_create(
                                product=product, display_order = images_count)
                            image.original.save(href.split('/')[-1],
                                            ContentFile(image_file.read()))
                            image.save()
                            images.append(image)
                            yield '\tattached image', 'SUCCESS'
                    else:
                        yield 'no image found', 'INFO'
            else:
                yield 'no items at search results', 'INFO'
    yield 'uploaded %s product images' % len(images), ''



            

def load_products_from_csv(data_file, row_ns=None):
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
    parsed_attributevalues = []
    product = None
    if row_ns:
        rows = filter(lambda r: not r[0] or ((r[0] + 1) in row_ns),
                      enumerate(reader))
    else:
        rows = enumerate(reader)
    # group all rows by upc
    upc_groups = {}
    for row_n, row in rows:
        if not header:
            header = [c.strip() for c in row]
            continue
        (upc, title, partner_sku, partner_code, partner_price,
        price, main_category, categories, desc) = (
            c.strip() for c in row[0:9])
        if not upc:
            continue
        group = upc_groups.get(upc, [])
        group.append({
            'upc': '%s%s' % ('0'*(10-len(str(upc))), upc),
            'title': title,
            'slug': slugify(u'%s_%s' % (title, upc)),
            'partner_sku': slugify(partner_sku),
            'partner_code': slugify(partner_code),
            'partner_price': partner_price,
            'price': price.replace(',', '.'),
            'main_category': main_category,
            'categories': categories,
            'desc': desc,
            'attributes': enumerate(row[9:])
        })
        upc_groups[upc] = group
    # iterate through groups and update db
    for upc, group in upc_groups.items():
        parent = None
        is_standalone = (len(group) == 1)
        for kwargs in group:
            slug = kwargs['slug']
            title = kwargs['title']
            product = None
            if not parent:
                # get parent for this group
                parent, __ = Product.objects.get_or_create(
                    upc=kwargs['upc'], 
                    structure=(
                        Product.STANDALONE
                        if is_standalone else
                        Product.PARENT),
                    defaults = {
                        'title': title,
                        'slug': slug,
                        'product_class': product_class
                    })
                # add category to parent 
                categories = tuple(kwargs['main_category'].split('\\'))
                parent_category = None
                category = None
                for i, category_name in enumerate(categories):
                    category_name = category_name.strip().capitalize()
                    category_slug = slugify(category_name)
                    qs = Category.objects.filter(
                                slug=category_slug, depth=i+1)
                    category = qs.first()
                    if not parent_category:
                        if not qs.exists():
                            category = Category.add_root(
                                    name=category_name, slug=category_slug)
                        else:
                            category = qs.first()
                    else:
                        for category in qs:
                            if category.get_parent() == parent_category:
                                break
                            category = None
                        if not category:
                            category = parent_category.add_child(
                                name=category_name, slug=category_slug)
                    parent_category = category
                if category:
                    ProductCategory.objects.get_or_create(
                        product=parent, category=category)
            # prepare attributes
            attribute_values = []
            found = ProductAttributeValue.objects.all()
            attributes = kwargs['attributes']
            for i, attribute_or_value in attributes:
                attribute_or_value = attribute_or_value.strip()
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
                    found = found & ProductAttributeValue.objects.filter(
                            product__parent=parent,
                            attribute=attribute,
                            value_text=value)
                    attribute_values.append((attribute, value))
            if not is_standalone: 
                # try to find child product with exactly the same attribute values
                from itertools import groupby
                for product, av in groupby(
                    found.order_by('product'), lambda f: f.product):
                    if ProductAttributeValue.objects.filter(
                            product=product).count() == len(
                                    list(av)):
                        break
                    else:
                        product = None
                if not product:
                    product = Product.objects.create(
                                parent=parent,
                                structure=Product.CHILD)
                else:
                    attribute_values = []
            else:
                product = parent
            # setting attributes for product
            for attribute, value in attribute_values: 
                attribute.save_value(product, value)
            # adding stockrecord
            partner_sku = kwargs['partner_sku'] 
            price = kwargs['price'] 
            partner_code = kwargs['partner_code']
            partner, __ = Partner.objects.update_or_create(
                        code=partner_code, defaults={'name': partner_code})
            if not partner_sku or partner.stockrecords.filter(
                    partner_sku=partner_sku).exists():
                partner_sku = ('%s_' % partner_sku) if partner_sku else ''
                partner_sku = '%s%s_%s_%s' % (
                        partner_sku, partner_code, upc,
                        partner.stockrecords.count())

            stockrecord, __ = StockRecord.objects.get_or_create(
                        product=product,
                        partner=partner,
                        defaults={
                            'partner_sku': partner_sku,
                            'num_in_stock': 100000,
                            'price_excl_tax': D(price)})
            yield product
