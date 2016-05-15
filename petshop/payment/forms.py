from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict

from petshop.core.forms import Form, ModelForm, PaymentRadioSelect

from .models import Source, Provider


class PaymentForm(ModelForm):

    class Meta:
        model = Source
        fields = ['source_type']
        widgets = {
            'source_type': PaymentRadioSelect
        }

    def __init__(self, shipping_method, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        queryset = shipping_method.get_payment_source_types()
        source_type = self.fields['source_type'] 
        source_type.queryset = queryset
        source_type.empty_label = None
        source_type.initial = queryset.first()
        source_type.label_from_instance = (
                lambda obj: format_html(
                    u'<span>{1}</span><img src="{0}"/>', obj.icon.url, obj.name))


class ProviderBaseForm(Form):

    def __init__(self, order, source, *args, **kwargs):
        super(ProviderBaseForm, self).__init__(*args, **kwargs)


class YandexKassaProviderForm(ProviderBaseForm):
    shopId = forms.IntegerField(widget=forms.HiddenInput)
    scid = forms.IntegerField(widget=forms.HiddenInput)
    sum = forms.DecimalField(widget=forms.HiddenInput)
    customerNumber = forms.IntegerField(widget=forms.HiddenInput)
    paymentType = forms.CharField(widget=forms.HiddenInput)
    orderNumber = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, order, source, *args, **kwargs):
        provider_settings = self.provider.settings
        user = order.basket.owner
        kwargs.update(initial={
            'shopId': provider_settings['shopId'],
            'scid': provider_settings['scid'], 
            'sum': order.total_incl_tax,
            'customerNumber': user.pk if user else 0,
            'paymentType': source.source_type.code,
            'orderNumber': order.number
        })
        super(YandexKassaProviderForm, self).__init__(
                    order, source, *args, **kwargs)


class YandexKassaProviderAdminForm(ModelForm):
    class Meta:
        model = Provider
        fields = []

    shopid = forms.CharField(label="shopId")
    scid = forms.CharField(label="scid")
    password = forms.CharField(label="shopPassword")
    port = forms.IntegerField(
            label=_("port for test mode"), min_value=0, required=False)
    schema = forms.ChoiceField(
            label=_("schema for test mode"),
            choices=(('https', 'https'), ('http', 'http')))
    url = forms.ChoiceField(
            choices = (
                (reverse_lazy('checkout:yandex_money_test'),
                 _('Inner testing')),
                ('https://demomoney.yandex.ru/eshop.xml',
                 _('Yandex.Kassa testing')),
                ('https://money.yandex.ru/eshop.xml',
                _('Yandex.Kassa')),
            ),
            label=_("Mode"), required=False)

    def __init__(self, *args, **kwargs):
        provider = kwargs.get('instance')
        if provider:
            kwargs.update(
                initial=dict(
                    shopid=provider.settings.get('shopId'),
                    scid=provider.settings.get('scid'),
                    password=provider.settings.get('shopPassword'),
                    url=provider.settings.get('url'),
                    port=provider.settings.get('port'),
                    schema=provider.settings.get('schema')
            ))
        (super(YandexKassaProviderAdminForm, self)
                .__init__(*args, **kwargs))

    def save(self, commit=True):
        provider = (
                super(YandexKassaProviderAdminForm, self).save(commit=False))
        provider.settings.update(
            shopId=self.cleaned_data.get('shopid'),
            scid=self.cleaned_data.get('scid'),
            shopPassword=self.cleaned_data.get('password'),
            url=self.cleaned_data.get('url'),
            port=self.cleaned_data.get('port'),
            schema=self.cleaned_data.get('schema'))
        if commit:
            provider.save()
        return provider
