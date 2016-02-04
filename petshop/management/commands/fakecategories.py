from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model
from oscar.core.utils import slugify

import random

from petshop.core.commands import FakeModelCommand


class Command(FakeModelCommand):
    CATEGORIES = (
            _('Clothes and footwear'),
            _('Dog toys'),
            _('Collars and leads'),
            _('Houses, kennels and mats'),
            _('Dog carriage equipment'),
    )

    model = get_model('catalogue', 'Category')
    default_count = 10
    bulk = False

    def get_model_kwargs(self, fake, default_fake, i):
        if i < len(self.CATEGORIES):
            name = self.CATEGORIES[i]
        else:
            name = u' '.join(fake.words(nb=random.randrange(1, 5)))
        kwargs = dict(
            name=name,
            description=fake.text(max_nb_chars=500),
            slug=slugify(name)
        )
        return kwargs

    def create_instance(self, dry_run, **kwargs):
        if not dry_run:
            o = self.model.add_root(**kwargs)
        return o
