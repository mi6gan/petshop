from django.conf import settings
from django.utils.translation import ugettext as _

from decimal import Decimal as D

from oscar.apps.shipping import methods
from oscar.core.loading import get_model


class ShippingMethodMixin(object):

	def get_payment_source_types(self):
		return get_model('payment', 'SourceType').objects.all().order_by('pk')
	
	@property
	def address_is_required(self):
		return True

	@property
	def address_required_fields(self):
		return ('first_name', 'last_name',
			    'phone_number', 'line1',
                'line4', 'postcode')


class RussianPost(ShippingMethodMixin, methods.Free):
	code = 'rupost'
	name = _('Free delivery by Russian Post')


class Courier(ShippingMethodMixin, methods.FixedPrice):
	code = 'courier'
	name = _('Delivery by courier in Moscow')
	charge_excl_tax = D('550.00')
	charge_incl_tax = D('550.00')

	@property
	def address_required_fields(self):
		return ('first_name', 'last_name',
			    'phone_number', 'line1')


class DHL(ShippingMethodMixin, methods.FixedPrice):
	code = 'dhl'
	name = _('Delivery by DHL in Russia')
	charge_excl_tax = D('1500.00')
	charge_incl_tax = D('1500.00')
