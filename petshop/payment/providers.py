from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.utils.functional import cached_property 
from django.utils.translation import ugettext_lazy as _

import os

from oscar.core.loading import get_model 

from .forms import ProviderBaseForm, YandexKassaProviderForm, YandexKassaProviderAdminForm


class ProviderBase(object):
    code = None
    name = None
    form_class = ProviderBaseForm
    admin_form_class = None
    settings = {} 
    source_types = ()
    source_types_icons = ()
    url = None
    _cache_key = 'provider__%s' % code

    def __init__(self):
        if not self.code or not self.form_class or not self.name:
            raise NotImplementedError("provide code, name and form class")
        self.form_class.provider = self

    def get_instance(self):
        instance = get_model('payment', 'Provider').objects.get_or_create(
                    code=self.code, defaults=dict(name=self.name,
                        settings=self.settings,
                        site=Site.objects.get_current()))[0]
        cache.set(self._cache_key, instance, 60)
        return instance

    @property
    def instance(self):
        cache_key = 'provider__%s' % self.code
        instance = cache.get(self._cache_key)
        if not instance:
            return self.get_instance()
        else:
            return instance

    def __unicode__(self):
        return unicode(self.name)


class YandexKassaProvider(ProviderBase):
    code = "yandex_kassa"
    name = _("Yandex.Kassa")
    form_class = YandexKassaProviderForm
    admin_form_class = YandexKassaProviderAdminForm
    settings = {
        "shopId": "117428",
        "scid": "532641",
        "shopPassword": "gahHaciep9qu",
        "url": reverse_lazy('checkout:yandex_money_test'),
        "port": "",
        "schema": "https"
    }
    source_types = (
        ('PC', _("Payment via a wallet in Yandex.Money")),
        ('AC', _("Payment via a bankcard")),
        #('WM', _("Payment via a wallet in WebMoney system")),
        ('GP', _("Cash via the terminal")),
        #('AB', _("Payment via Alfa-Click")),
        #('CR', _("Cash payment at delivery"))
    )

    source_types_icons = (
        ('PC', 'petshop/payment/PC.png'),
        ('AC', 'petshop/payment/AC.png'),
        #('WM', 'petshop/payment/WM.png'),
        ('GP', 'petshop/payment/GP.png'),
        #('AB', 'petshop/payment/AB.png'),
        #('CR', 'petshop/payment/GP.png')
    )

    @property
    def url(self):
        return self.instance.settings.get('url')


class DefaultProvider(ProviderBase):
    code = "default"
    name = _("Default provider")
    url = reverse_lazy('payment:provider_default')
    source_types = (
        ('DF', _("Pay at the delivery of product")),
    )
    source_types_icons = (
        ('DF', 'petshop/payment/GP.png'),
    )


class ProvidersPool(object):

    providers = [DefaultProvider(), YandexKassaProvider()]

    def preload_providers(self):
        for provider in self.providers:
            if provider.instance:
                pass

    def preload_types(self):
        for provider in self.providers:
            SourceType = get_model('payment', 'SourceType')
            icons = dict(provider.source_types_icons)
            for code, name in provider.source_types:
                SourceType.objects.update_or_create(
                    code=code,
                    provider=provider.instance, 
                    defaults=dict(name=name,
                    icon=os.path.join(settings.MEDIA_URL, icons.get(code))))

    def get_by_code(self, code):
        for provider in self.providers:
            if provider.code == code:
                return provider

providers_pool = ProvidersPool()
