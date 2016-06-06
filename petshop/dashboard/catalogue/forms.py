from django import forms
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model


class ProductSearchForm(forms.Form):
    upc = forms.CharField(max_length=16, required=False, label=_('UPC'))
    title = forms.CharField(
        max_length=255, required=False, label=_('Product title'))
    partner_sku = forms.CharField(
            max_length=32, required=False, label=_('Partner SKU'))
    partner = forms.ModelChoiceField(
            queryset = get_model('partner', 'Partner').objects.all(),
            required=False, label=_('Partner'))
    has_image = forms.ChoiceField(
            choices=(
                ('', _('-'*10)),
                ('1', _('Yes')),
                ('2', _('No'))
            ),
            required=False, label=_('With image'))

    def clean(self):
        cleaned_data = super(ProductSearchForm, self).clean()
        cleaned_data['upc'] = cleaned_data['upc'].strip()
        cleaned_data['title'] = cleaned_data['title'].strip()
        cleaned_data['partner_sku'] = cleaned_data['partner_sku'].strip()
        return cleaned_data
