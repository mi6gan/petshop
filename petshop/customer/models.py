from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from oscar.apps.customer.abstract_models import AbstractCommunicationEventType


class CommunicationEventType(AbstractCommunicationEventType):

    staff = models.ManyToManyField(
            settings.AUTH_USER_MODEL, verbose_name=_('Managers'), blank=True)
    



from oscar.apps.customer.models import *  # noqa
