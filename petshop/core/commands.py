from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.db.utils import IntegrityError

import random

from faker import Factory


class FakeModelCommand(BaseCommand):

    model = None
    default_count = 100
    bulk = True

    def add_arguments(self, parser):
            parser.add_argument('--count',
                            default=self.default_count, type=int)
            parser.add_argument('--dry-run', action='store_true')
            parser.add_argument('--delete', action='store_true')

    def handle(self, verbosity, count, dry_run, delete, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)
        if delete:
            qs = self.get_delete_queryset()
            n = qs.count()
            qs.delete()
            self.stdout.write(_('Deleted %s %s(s)') % 
                        (n, self.model._meta.verbose_name))
            return
        fakes = [Factory.create(lang[0])
                  for lang in settings.LANGUAGES]
        default_fake = Factory.create()
        objects = []
        for i in range(count):
            fake = random.choice(fakes)
            self.stdout.write(self.style.NOTICE(u'%s #%s') % 
                              (self.model._meta.verbose_name, i+1))
            while True:
                kwargs = self.get_model_kwargs(fake, default_fake, i)
                if verbosity>1:
                    self.stdout.write((u'\n').join(u'%s\n%s' % 
                            (self.style.SQL_FIELD(kv[0]), kv[1] or 'NULL') 
                            for kv in kwargs.items()))
                    self.stdout.write('')
                try:
                    o = self.create_instance(dry_run, **kwargs)
                    objects.append(o)
                    break
                except IntegrityError as e:
                    self.stderr.write(self.style.ERROR(u'%s\n' %
                                        e.message.decode('utf-8')))
                except ValidationError as errors:
                    for field, messages in errors:
                         self.stderr.write(self.style.ERROR(u'%s: %s\n' % 
                                                (field, u'\n'.join(messages))))
            self.stderr.write('\n')
        if not dry_run and self.bulk:
            self.model.objects.bulk_create(objects)
            n = len(objects)
            self.stdout.write(_('Created %s %s(s)') % 
                    (n, self.model._meta.verbose_name))
        if not dry_run:
            self.postprocess_objects(objects, fake, default_fake)

    def create_instance(self, dry_run, **kwargs):
        o = self.model(**kwargs)
        if not self.bulk and not dry_run:
            o.save()
        else:
            o.full_clean()
        return o

    def postprocess_objects(self, objects, fake, default_fake):
        pass

    def get_delete_queryset(self):
        return self.model.objects.all()

    def get_model_kwargs(self, fake, default_fake, i):
        raise NotImplementedError
