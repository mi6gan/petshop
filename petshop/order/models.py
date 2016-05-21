from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible, smart_text, force_text

from oscar.apps.order.abstract_models import AbstractOrder


class Order(AbstractOrder):
    STATUS_PENDING = 'pending'
    STATUS_CHECKED = 'checked'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = (
        (STATUS_PENDING, _('Pending for payment')),
        (STATUS_CHECKED, _('Checked')),
        (STATUS_PAID, _('Paid')),
        (STATUS_FAILED, _('Payment is not submitted'))
    )

    def shipping_address_summary(self):
        return u", ".join(filter(
            len, self.shipping_address.active_address_fields()))


Order._meta.get_field('status')._choices = Order.STATUS_CHOICES


from oscar.apps.order.models import *  # noqa
