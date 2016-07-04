from django.conf import settings
from django.utils.translation import ugettext as _

from decimal import Decimal as D

from oscar.apps.shipping import methods
from oscar.core.loading import get_model


class ShippingMethodMixin(object):

	def get_payment_source_types(self):
		return get_model('payment', 'SourceType').objects.filter(
                provider__enabled=True).order_by('pk')
	
	@property
	def address_is_required(self):
		return True

	@property
	def address_required_fields(self):
		return ('first_name', 'last_name', 'middle_name',
			    'phone_number', 'line1',
                'line4', 'postcode')


class RussianPost(ShippingMethodMixin, methods.Free):
	code = 'rupost'
	name = _('Delivery by Russian Post')
