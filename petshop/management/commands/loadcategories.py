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
        is_new = False
        prev_depth = 0
        for name in categories_file.readlines():
            name = name.decode('utf-8')
            depth = len(tabs_re.findall(name))
            if depth <= prev_depth:
                is_new = False
            name, info = name.split(':')
            new_name = name
            if info:
                parts = info.split()
                if parts[0] == 'rename':
                    new_name = (' '.join(parts[1:])).strip()
                elif parts[0] == 'new':
                    is_new = True
            kwargs = dict(
                name=name,
                slug=slugify(name))
            if depth>=1 and len(parents)>=1:
                if depth + 1 < len(parents):
                    parents = parents[:depth + 1]
                if depth + 1 > len(parents):
                    if is_new:
                        child = parents[-1].add_child(**kwargs)
                    else:
                        child = parents[-1].get_children().get(
                                depth=depth, name__iexact__contains=name)
                        child.move(parents[-1], pos='last-child')
                    parents.append(child)
                elif depth + 1 == len(parents):
                    if is_new:
                        sibling = parents[-1].add_sibling(**kwargs)
                    else:
                        sibling = parents[-1].get_siblings().get(
                                depth=depth, name__iexact__contains=name)
                        sibling.move(sibling.get_parent(), pos='last-child')
            else:
                if is_new:
                    root = Category.add_root(**kwargs)
                else:
                    root = Category.objects.get(
                            depth=depth, name__iexact__contains=name)
                parents = [root]
