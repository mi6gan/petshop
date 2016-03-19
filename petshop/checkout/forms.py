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
                charge = int(method.calculate(basket).excl_tax),
                address = method.address_required_fields + ('email',))

        self.fields['method_code'].widget = (StyledRadioSelect(
            choices=choices,
            attrs={
                'data-extra': json.dumps(data_extra),
                'data-addressformprefix': 'addressform'
            }
        ))
        self.fields['method_code'].initial = shipping_methods[0].code 


Country = get_model('address', 'country')

ADDRESS_FIELDS_INITIAL = {
    'line1': _('No address required'),
    'line4': _('Moscow'),
    'country': Country.objects.get(iso_3166_1_a2='RU'),
    'postcode': '117133' 
}


class ShippingAddressForm(ModelForm, OscarShippingAddressForm):
    class Meta:
        model = OscarShippingAddressForm.Meta.model
        fields = [
                'country', 'state',
                'first_name', 'last_name', 'phone_number',
                'line4', 'line1', 'postcode', 
        ]
        labels = {
            'line1': _('Address'),
            'line4': _('City')
        }
        widgets = {
            'phone_number': PhoneNumberMaskWidget() 
        }
    email = forms.EmailField(label=_('Email'))

    def __init__(self, shipping_method, guest_email=None, *args, **kwargs):
        required_fields = getattr(shipping_method, 'address_required_fields', [])
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        if guest_email:
            self.fields['email'].initial = guest_email
        for field_name in self.fields:
            required = field_name in required_fields
            if not required and not field_name in ['email']:
                self.fields[field_name].widget = forms.HiddenInput()
                self.fields[field_name].initial = (
                    ADDRESS_FIELDS_INITIAL.get(field_name))
                print field_name, self.fields[field_name].initial
            else:
                self.fields[field_name].widget.attrs[
                    'placeholder'] = self.fields[field_name].label
                self.fields[field_name].required = required
            if field_name in ADDRESS_FIELDS_INITIAL: 
                self.fields[field_name].widget.attrs['data-initial'] = (
                        ADDRESS_FIELDS_INITIAL[field_name])
        original_fields = self.fields
        print original_fields
        self.fields = OrderedDict([('email', self.fields['email']),] + 
                                [(k, v) for k, v in self.fields.items()
                                                 if k not in ['email']])


class CheckoutBaseForm(BaseCombinedForm):

    def __init__(self, basket, shipping_method, *args, **kwargs):
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
            user_address = user.addresses.first()
            if user_address:
                addressform_initial = {
                    f: getattr(user_address, f)
                    for f in ShippingAddressForm.Meta.fields  
                }
                addressform_initial.update(email=user.email)
        kwargs.update({
            'shippingform__kwargs': {
                'basket': basket
            },
            'addressform__kwargs': {
                'shipping_method': shipping_method
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
