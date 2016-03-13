from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model

from requests import Session

import random
import os
import re


class Command(BaseCommand):

    def soup_from_url(self, domain, url):
        response = self.session.get('http://%s/%s' % (domain, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def handle_kaskad(self):
        domain = 'kaskad-pet.ru'
        for category_link in list_page.select('.catalog>.tovar>a'):
            category_page = self.soup_from_url(domain, category_link.href)
            for product_link in (
                    category_page.select('.catalog .desc>.desc_kat')):
                product_page = self.soup_from_url(domain, product_link.href)
                product = {}
                for prop_block in product.select('ul.property > li'):
                    text = prop_block.get_text()
                    if text.strip() == 'Код товара:':
                        product['code'] = text

    def handle(self, *args, **kwargs):
        super(Command, self).handle(*args, **options)
        self.session = Session()
