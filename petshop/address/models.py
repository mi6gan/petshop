from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from oscar.apps.address.abstract_models import (
        AbstractUserAddress, AbstractShippingAddress)


class UserAddress(AbstractUserAddress): 
    middle_name = models.CharField(_("Middle name"), max_length=255, blank=True)


class ShippingAddress(AbstractShippingAddress):
    middle_name = models.CharField(_("Middle name"), max_length=255, blank=True)


from oscar.apps.address.models import *  # noqa
