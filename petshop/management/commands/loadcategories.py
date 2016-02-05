from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.management.base import BaseCommand

from oscar.core.loading import get_model
from oscar.core.utils import slugify

import random
import os
import re


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        file_path = os.path.join(
                settings.BASE_DIR, 'petshop', 'fixtures', 'categories.txt')
        categories_file = open(file_path, 'r')
        Category = get_model('catalogue', 'Category')
        parents = []
        tabs_re = re.compile(r'\t|[\s]{4}')
        for name in categories_file.readlines():
            name = name.decode('utf-8')
            depth = len(tabs_re.findall(name))
            name = name.strip()
            kwargs = dict(
                name=name,
                slug=slugify(name))
            if depth>=1 and len(parents)>=1:
                if depth + 1 < len(parents):
                    parents = parents[:depth + 1]
                if depth + 1 > len(parents):
                    child = parents[-1].add_child(**kwargs)
                    parents.append(child)
                elif depth + 1 == len(parents):
                        sibling = parents[-1].add_sibling(**kwargs)
                        parents[-1] = sibling
            else:
                root = Category.add_root(**kwargs)
                parents = [root]
