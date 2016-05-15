from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict
import json

from oscar.apps.checkout.forms import (
        ShippingAddressForm as OscarShippingAddressForm)
from oscar.core.loading import get_model, get_class

from petshop.core.forms import (
        Form, ModelForm, PhoneNumberMaskWidget, PaymentRadioSelect,
        StyledRadioSelect, BaseCombinedForm, combinedform_factory)


Repository = get_class('shipping.repository', 'Repository')
PaymentForm = get_class('payment.forms', 'PaymentForm')
PetshopAddressForm = get_class('address.forms', 'PetshopAddressForm')
ShippingAddress = get_model('order', 'ShippingAddress')


class ShippingMethodsForm(Form):

    class Media:
        js = ('js/forms/basket.summary.js',)

    method_code = forms.CharField()

    def __init__(self, basket, *args, **kwargs):
        super(ShippingMethodsForm, self).__init__(*args, **kwargs)
        repo = Repository()
        shipping_methods = repo.get_available_shipping_methods(basket)
        choices = []
        data_extra = {}
        for method in shipping_methods:
            choices.append((method.code, method.name))
            data_extra[method.code] = dict(
                charge = int(method.calculate(basket).incl_tax),
                address = method.address_required_fields + ('email',))

        self.fields['method_code'].widget = (StyledRadioSelect(
            choices=choices,
            attrs={
                'data-extra': json.dumps(data_extra),
                'data-addressformprefix': 'addressform'
            }
        ))
        self.fields['method_code'].initial = shipping_methods[0].code 


class ShippingAddressForm(ModelForm, PetshopAddressForm):

    class Meta(PetshopAddressForm.Meta):
        model = ShippingAddress 

    def __init__(self, shipping_method, *args, **kwargs):
        required_fields = getattr(
            shipping_method, 'address_required_fields', [])
        super(ShippingAddressForm, self).__init__(
                    required_fields, *args, **kwargs)


class CheckoutBaseForm(BaseCombinedForm):

    def __init__(self, basket, shipping_method, address=None, *args, **kwargs):
        shipping_kwargs = kwargs.copy()
        shipping_kwargs['prefix'] = "shippingform"
        shippingform = ShippingMethodsForm(basket, *args, **shipping_kwargs)
        if shippingform.is_valid():
            method_code = shippingform.cleaned_data.get('method_code')
            if method_code:
                shipping_method = (
                        Repository().get_shipping_method_by_code(method_code))
        addressform_initial = None
        user = basket.owner
        if user:
            shipping_useraddress = user.addresses.filter(
                is_default_for_shipping=True).first()
            if shipping_useraddress:
                addressform_initial = {
                    f: getattr(shipping_useraddress, f)
                    for f in ShippingAddressForm.Meta.fields  
                }
        kwargs.update({
            'shippingform__kwargs': {
                'basket': basket
            },
            'addressform__kwargs': {
                'shipping_method': shipping_method,
                'initial': addressform_initial
            },
            'paymentform__kwargs': {
                'shipping_method': shipping_method
            }
        })
        if addressform_initial:
            kwargs['addressform__kwargs']['initial'] = addressform_initial
        super(CheckoutBaseForm, self).__init__(*args, **kwargs)

    def addressform_subclean(self, form):
        shipping_method = (
                self.shippingform.cleaned_data.get('shipping_method'))
        if shipping_method:
            address_required_fields = (
                getattr(shipping_method, 'address_required_fields', []))
            for field in address_required_fields:
                value = form.cleaned_data.get(field)
                if not value:
                    self.add_error('%s-%s' % (form.prefix, field),
                                   forms.ValidationError(
                                       _('This field can\'t be empty')))


CheckoutForm = combinedform_factory([
                    ('shippingform', ShippingMethodsForm),
                    ('addressform', ShippingAddressForm),
                    ('paymentform', PaymentForm)], CheckoutBaseForm)
