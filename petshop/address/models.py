from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from oscar.apps.address.abstract_models import (
        AbstractUserAddress, AbstractShippingAddress)


class AddressMixin(models.Model):
    
    class Meta:
        abstract = True

    middle_name = models.CharField(_("Middle name"), max_length=255, blank=True)

    @property
    def salutation(self):
        return self.join_fields(
            ('title', 'last_name', 'first_name', 'middle_name'),
            separator=u" ")

    def active_address_fields(self, include_salutation=True):
        fields = [self.line1, self.line2, self.line3,
                  self.line4, self.state, self.postcode]
        if include_salutation:
            fields = [self.salutation] + fields
        fields = [f.strip() for f in fields if f]
        try:
            fields.append(self.country.name)
        except exceptions.ObjectDoesNotExist:
            pass
        return fields


class UserAddress(AbstractUserAddress, AddressMixin):
    pass


class ShippingAddress(AbstractShippingAddress, AddressMixin):
    pass


from oscar.apps.address.models import *  # noqa
