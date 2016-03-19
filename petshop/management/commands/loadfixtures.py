from django.core.management.base import BaseCommand
from django.core.management.commands.loaddata import Command as LoadDataCommand
from django.db import DEFAULT_DB_ALIAS

from petshop.payment.providers import providers_pool


class Command(BaseCommand):

    model = None
    default_count = 100

    def add_arguments(self, parser):
        parser.add_argument('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to load '
            'fixtures into. Defaults to the "default" database.')
        parser.add_argument('--app', action='store', dest='app_label',
            default=None, help='Only look for fixtures in the specified app.')
        parser.add_argument('--ignorenonexistent', '-i', action='store_true',
            dest='ignore', default=False,
            help='Ignores entries in the serialized data for fields that do not '
            'currently exist on the model.')

    def handle(self, *args, **options):
        loaddata = LoadDataCommand()
        loaddata_options = {
            'ignore': options.get('ignore'),
            'database': options.get('database'),
            'app_label': options.get('app_label'),
            'hide_empty': options.get('hide_empty', False),
            'verbosity': options.get('verbosity')
        }
        fixture_labels = ['sites', 'cms', 'menus',
                          'easy_thumbnails', 'filer',
                          'auth', 'petshop']
        providers_pool.preload_providers()
        providers_pool.preload_types()
        loaddata.handle(*fixture_labels, **loaddata_options)
