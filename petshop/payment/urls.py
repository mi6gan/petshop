from django.conf.urls import *  # NOQA

from .views import YandexMoneyCheckView, YandexMoneyAvisoView, DefaultProviderView

urlpatterns = [
    url(r'^yk-check/$', YandexMoneyCheckView.as_view(), name='yandex_money_check'),
    url(r'^yk-aviso/$', YandexMoneyAvisoView.as_view(), name='yandex_money_aviso'),
    url(r'^providers/default/$', DefaultProviderView(), name='provider_default'),
]
