from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from oscar.apps.checkout.app import CheckoutApplication

from .views import (
        CheckoutView, PaymentView, YandexMoneyTestView, OrderPaymentView)


class PetshopCheckoutApplication(CheckoutApplication):

    def get_urls(self):
        urls = [
             url(r'^$', CheckoutView.as_view(), name='index'),
             url(r'^payment/$', PaymentView.as_view(), name='payment'),
             url(r'^payment/(?P<number>\d+)$', OrderPaymentView.as_view(), name='order_payment'),
             url(r'^yandex-money-test/$', YandexMoneyTestView.as_view(), name='yandex_money_test'),
        ]
        return self.post_process_urls(urls)


application = PetshopCheckoutApplication()
