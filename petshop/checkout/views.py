from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Sum
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property 
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, DetailView, View
from django.views.decorators.cache import never_cache

import datetime
import requests

from oscar.apps.checkout.views import PaymentDetailsView
from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.core.loading import get_class, get_model

from decimal import Decimal as D

from petshop.core.views import AjaxFormView
from petshop.core.utils import (
        send_email_to, send_email_to_managers,
        send_email_to_admins, yandex_money_checksum)
from petshop.payment.providers import providers_pool

from .forms import CheckoutForm

Repository = get_class('shipping.repository', 'Repository')
Order = get_model('order', 'Order')
OrderCreator = get_class('order.utils', 'OrderCreator')
OrderTotalCalculator = get_class(
            'checkout.calculators', 'OrderTotalCalculator')
SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
UserAddress = get_model('address', 'UserAddress')

class CheckoutSessionMixin(object):

    @property
    def payment_provider(self):
        return providers_pool.get_by_code('yandex_kassa')

    session_key = 'checkout_session' 
    checkout_urls = [
        'checkout:index',
        'checkout:payment'
    ]
    checks = [
        'basket_is_valid',
        'basket_is_not_empty',
        'order_is_placed',
        'has_payment_source'
    ]

    def reset_session(self):
        try:
            if not isinstance(self.request.session.get(self.session_key), dict):
                order = None
            else:
                order = self.get_order()
        except Order.DoesNotExist:
            order = None
        self.request.session[self.session_key] = {}
        if order:
            self._set_model_instance('placed_order', order)

    @property
    def session(self):
        if not isinstance(self.request.session.get(self.session_key), dict):
            self.reset_session()
        return self.request.session[self.session_key]

    def _get_model_instance(self, name, model):
        protected_name = '_%s' % name
        if not hasattr(self, protected_name):
            pk = self.session.get(name)
            setattr(self, protected_name, model.objects.get(pk=pk))
        return getattr(self, protected_name)

    def _set_model_instance(self, name, instance):
        self.session[name] = instance.pk
        setattr(self, '_%s' % name, instance)

    def check(self):
        return all(getattr(self, 'check_%s' % c)() for c in self.checks)

    def get_checkfailed_url(self):
        current_url = self.request.resolver_match.view_name
        prev_url = self.checkout_urls[0]
        for url in self.checkout_urls:
            if current_url == url:
                break
            prev_url = url
        return reverse(prev_url)

    def get_success_url(self):
        current_url = self.request.resolver_match.view_name
        next_url = self.checkout_urls[0]
        for url in reversed(self.checkout_urls):
            if current_url == url:
                break
            next_url = url
        self.request.session.save()
        return reverse(next_url)

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if not self.check():
            return HttpResponseRedirect(self.get_checkfailed_url())
        return (super(CheckoutSessionMixin, self)
                .dispatch(request, *args, **kwargs))

    def get_order(self):
        return self._get_model_instance('order', Order)

    def get_placed_order(self):
        return self._get_model_instance('placed_order', Order)

    def get_payment_source(self):
        return self._get_model_instance('payment_source', Source)

    def set_order(self, order):
        self.reset_session()
        self._set_model_instance('order', order)
        self._set_model_instance('payment_source', order.sources.first())

    def place_order(self, **kwargs):
        try:
            order = self.get_order()
            self.reset_session()
        except Order.DoesNotExist:
            pass
        order = OrderCreator().place_order(**kwargs)
        order.basket.submit()
        self._set_model_instance('order', order)
        ctx = dict(order=order)
        send_email_to_managers(self.request, 'ORDER_PLACED', ctx)
        return order

    def add_payment_source(self, source_type, total=False):
        order = self.get_order()
        payment_source, __ = Source.objects.get_or_create(
                order=order, source_type=source_type)
        if total:
            payment_source.allocate(total)
        self._set_model_instance('payment_source', payment_source)
        return payment_source

    def check_basket_is_valid(self):
        """
        Check that the basket is permitted to be submitted as an order. That
        is, all the basket lines are available to buy - nothing has gone out of
        stock since it was added to the basket.
        """
        strategy = self.request.strategy
        success = True
        for line in self.request.basket.all_lines():
            result = strategy.fetch_for_line(line)
            is_permitted, reason = result.availability.is_purchase_permitted(
                line.quantity)
            if not is_permitted:
                # Create a more meaningful message to show on the basket page
                success = False
                msg = _(
                    "'%(title)s' is no longer available to buy (%(reason)s). "
                    "Please adjust your basket to continue"
                ) % {
                    'title': line.product.get_title(),
                    'reason': reason}
                messages.error(self.request, msg)
        return success

    def check_basket_is_not_empty(self):
        if self.request.basket.is_empty:
            messages.error(self.request,
                    _("You need to add some items to your basket to checkout")
            )
            return False
        else:
            return True

    def check_order_is_placed(self):
        try:
            self.get_order()
            return True
        except Order.DoesNotExist:
            messages.error(self.request, _("Current order is not placed yet"))
            return False

    def check_has_payment_source(self):
        try:
            self.get_payment_source()
            return True
        except PaymentSource.DoesNotExist:
            messages.error(self.request, _("Payment source is not selected yet"))
            return False


class CheckoutView(CheckoutSessionMixin, AjaxFormView):
    form_class = CheckoutForm
    http_method_names = ['post']
    checks = [
        'basket_is_valid',
        'basket_is_not_empty',
    ]

    def form_valid(self, form):
        user = self.request.user
        shipping_form = form.shippingform
        address_form = form.addressform
        payment_form = form.paymentform
        shipping_method_code = (
            shipping_form.cleaned_data.get('method_code'))
        if shipping_method_code:
            repo = Repository()
            shipping_method = (
                    repo.get_shipping_method_by_code(shipping_method_code))
            address_fields = dict(
                (k, v) for (k, v) in address_form.instance.__dict__.items()
                if not k.startswith('_'))
        shipping_address = address_form.save()
        if user.is_authenticated():
            useraddress = UserAddress(**{
                f.name: getattr(shipping_address, f.name)
                for f in UserAddress._meta.get_fields()
                if hasattr(shipping_address, f.name)
            })
            if not user.addresses.filter(
                    hash=useraddress.generate_hash()).exists():
                useraddress.user = user
                if not user.addresses.filter(
                    is_default_for_shipping=True).exists():
                    useraddress.is_default_for_shipping = True
                    useraddress.save()
        basket = self.request.basket
        shipping_charge = shipping_method.calculate(basket)
        total = OrderTotalCalculator().calculate(basket, shipping_charge)
        order = self.place_order(
                user=self.request.user,
                basket=basket,
                total=total,
                shipping_method=shipping_method,
                shipping_charge=shipping_charge,
                shipping_address=shipping_address)
        source = self.add_payment_source(
                payment_form.instance.source_type, total.incl_tax)
        response = {
            'success_url': self.get_success_url(),
            'result': 'ok'
        }
        return JsonResponse(response)

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CheckoutView, self).get_form_kwargs(**kwargs)
        repo = Repository()
        basket = self.request.basket
        shipping_method = repo.get_shipping_methods(basket)[0]
        kwargs.update(
                basket=basket, 
                shipping_method=shipping_method)
        return kwargs


class PaymentView(CheckoutSessionMixin, FormView):
    checks = [
        'order_is_placed',
        'has_payment_source'
    ]
    template_name = "checkout/payment.html"

    def get_form_class(self):
        return self.payment_provider.form_class

    def dispatch(self, request, *args, **kwargs):
        if not self.check():
            return HttpResponseRedirect(self.get_checkfailed_url())
        order = self.get_order()
        source = self.get_payment_source()
        status = order.status
        total = order.total_incl_tax
        if not status or status == Order.STATUS_PENDING:
            amount_debited = (
                    order.sources.aggregate(
                        amount=Sum('amount_debited'))['amount']) or 0
            if amount_debited >= total:
                order.status = Order.STATUS_PAID
                order.save()
                ctx = dict(order=order, source=source)
                send_email_to_managers(self.request, 'ORDER_PAID', ctx)
                send_email_to(
                        self.request, 'USER_ORDER_PAID', ctx, [order.email])
        if order.status == Order.STATUS_FAILED:
            messages.error(self.request, 
                        mark_safe(
                            _("Sorry, but the payment is not submitted yet."
                          " Don't worry, we're already"
                          " processing it as order #{0}."
                          " You may want to"
                          " <a href='{1}'>retry your payment</a> or just wait"
                          " and our managers will contact you soon."
                          ).format( order.number, reverse(
                              'checkout:order_payment', args=[order.number]))))
        elif order.status == Order.STATUS_PAID:
                messages.success(self.request, 
                        _("Thank you! Your order #{0}"
                          " is successfully paid."
                          " Please wait for our managers response,"
                          " they will contact you soon.").format(order.number))
        if order.status in (Order.STATUS_PAID, Order.STATUS_FAILED):
            self.reset_session()
            if request.user.is_authenticated():
                return redirect('customer:order', order.number)
            else:
                return redirect('customer:anon-order',
                        order.number, order.verification_hash())
        else:
            return (super(PaymentView, self)
                        .dispatch(request, *args, **kwargs))

    def get_form_kwargs(self):
        kwargs = super(PaymentView, self).get_form_kwargs()
        kwargs.update(order=self.get_order(), source=self.get_payment_source())
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(PaymentView, self).get_context_data(**kwargs)
        kwargs.update(provider=self.payment_provider)
        return kwargs


class OrderPaymentView(CheckoutSessionMixin, DetailView):
    http_method_names = ['get']
    model = Order
    checks = []
    slug_field = 'number' 
    slug_url_kwarg = 'number'

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = Order.STATUS_PENDING
        order.save()
        self.set_order(order)
        payment_source = order.sources.first()
        self.add_payment_source(
                payment_source.source_type, max(
                    order.total_incl_tax,
                    payment_source.amount_allocated))
        return redirect('checkout:payment')


class YandexMoneyTestView(CheckoutSessionMixin, TemplateView):
    template_name = 'checkout/yandex_money_test.html'
    checks = [
        'order_is_placed',
        'has_payment_source'
    ]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not self.check():
            return HttpResponseRedirect(self.get_checkfailed_url())
        return (super(YandexMoneyTestView, self)
                .dispatch(request, *args, **kwargs))

    def send_data(self, action, order, source, fail=False):
        session = requests.Session()
        local_now = timezone.localtime(timezone.now())
        provider_settings = source.source_type.provider.settings
        request_datetime = datetime.datetime.isoformat(timezone.now())
        data = dict(
            action=action,
            orderSumAmount=order.total_incl_tax,
            orderSumCurrencyPaycash=643,
            orderSumBankPaycash=643,
            shopId=provider_settings.get('shopId'),
            invoiceId=source.pk,
            customerNumber=(
                self.request.user.pk 
                if self.request.user.is_authenticated() else 0))

        md5_data = data.copy()
        if not fail:
            md5_data.update(
                shopPassword=provider_settings['shopPassword'])

        data.update(
            requestDatetime=request_datetime,
            orderNumber=order.number,
            orderCreatedDatetime=request_datetime,
            shopSumAmount=order.total_incl_tax,
            paymentType=source.source_type.code,
            md5=yandex_money_checksum(**md5_data)
        )
        site = get_current_site(self.request)
        if action == 'paymentAviso':
            data.update(
                paymentDatetime=request_datetime,
                cps_user_country_code='RU')
            url = reverse('payment:yandex_money_aviso')
        else:
            url = reverse('payment:yandex_money_check')
        schema = provider_settings.get('schema', 'https')
        port =  provider_settings.get('port', False) or ''
        if port:
            port = ':%s' % port
        return session.post('%s://%s%s%s' % (
            schema, site.domain, port, url), data, verify=False)


    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', False)
        if action:
            order = self.get_order()
            source = self.get_payment_source()
            self.send_data('checkOrder', order, source, action=='fail')
            self.send_data('paymentAviso', order, source, action=='fail')
            return redirect('checkout:payment')
        else:
            return (super(YandexMoneyTestView, self)
                    .get(request, *args, **kwargs))
