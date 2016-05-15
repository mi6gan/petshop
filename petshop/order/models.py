from django.utils.translation import ugettext_lazy as _

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

    def get_status_display(self):
        return dict(Order.STATUS_CHOICES).get(self.status, _('Unknown'))

    def shipping_address_summary(self):
        return u", ".join(filter(
            len, self.shipping_address.active_address_fields()))


from oscar.apps.order.models import *  # noqa
