from django import forms
from django.utils.translation import ugettext_lazy as _

from oscar.apps.address.forms import AbstractAddressForm
from oscar.core.loading import get_model

from petshop.core.forms import (
        Form, ModelForm, PhoneNumberMaskWidget)


UserAddress = get_model('address', 'UserAddress')
Country = get_model('address', 'country')

ADDRESS_FIELDS_INITIAL = {
    'line1': _('No address required'),
    'line4': _('Moscow'),
    'country': Country.objects.get(iso_3166_1_a2='RU'),
    'state': _('Moscow'),
    'postcode': '117133' 
}


class PetshopAddressForm(AbstractAddressForm):

    class Meta:
        fields = [
                'country', 'state',
                'last_name', 
                'first_name',
                'middle_name', 
                'phone_number',
                'line4', 'line1', 'postcode', 
        ]
        labels = {
            'line1': _('Address'),
            'line4': _('City')
        }
        widgets = {
            'phone_number': PhoneNumberMaskWidget()
        }

    def __init__(self, required_fields=None, *args, **kwargs):
        super(PetshopAddressForm, self).__init__(*args, **kwargs)
        if not required_fields:
            required_fields = self.fields.keys()
            required_fields.remove('country')
            required_fields.remove('state')
        for field_name in self.fields:
            required = field_name in required_fields
            if not required:
                self.fields[field_name].widget = forms.HiddenInput()
                self.fields[field_name].initial = (
                    ADDRESS_FIELDS_INITIAL.get(field_name))
            else:
                self.fields[field_name].widget.attrs[
                    'placeholder'] = self.fields[field_name].label
                self.fields[field_name].required = required
            if field_name in ADDRESS_FIELDS_INITIAL: 
                self.fields[field_name].widget.attrs['data-initial'] = (
                        ADDRESS_FIELDS_INITIAL[field_name])


class UserAddressForm(ModelForm, PetshopAddressForm):

    class Meta(PetshopAddressForm.Meta):
        model = UserAddress

    def __init__(self, user, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        self.instance.user = user
