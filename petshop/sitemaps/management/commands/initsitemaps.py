# -*- coding: utf-8 -*-
from cms.models import Page
from petshop.sitemaps import sitemaps

from django.core.management.base import BaseCommand 
from django.conf import settings
from django.utils import translation
from django.utils.encoding import smart_text

from optparse import make_option


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
                '-e', '--exclude', dest='exclude',
                action='append', default=[],
            help='A model name to exclude')

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        exclude = options.get('exclude')
        translation.activate(settings.LANGUAGE_CODE)
        for model in (Page,):
            if verbosity > 2:
                self.stdout.write(smart_text('Saving all instances'
                    ' of %s one by one,'
                    ' to trigger post_save signals') % model)
            for obj in model.objects.all():
                obj.save()
                if verbosity > 2:
                    if hasattr(obj, 'sitemap_node') and obj.sitemap_node:
                        self.stdout.write(smart_text('Sitemap node'
                                ' for %s now is %s') % (
                                    obj, obj.sitemap_node))
                    else:
                        self.stdout.write(
                                smart_text('No sitemap node for %s') % obj)
