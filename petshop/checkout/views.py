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
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property 
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, DetailView, View
from django.views.generic.base import TemplateResponseMixin
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

class CheckoutSessionMixin(object):

    payment_provider = cached_property(
            lambda self: providers_pool.get_by_code('yandex_kassa'))

    session_key = 'checkout_session' 
    checkout_urls = [
        'basket:summary',
        'checkout:checkout',
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

    def add_payment_source(self, source_type):
        order = self.get_order()
        payment_source, __ = Source.objects.get_or_create(
                order=order, source_type=source_type)
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
        # shipping address
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
                payment_form.instance.source_type)
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
        kwargs.update(basket=basket, shipping_method=shipping_method)
        return kwargs


class PaymentView(CheckoutSessionMixin, FormView):
    checks = [
        'order_is_placed',
        'has_payment_source'
    ]
    template_name = "oparts/checkout/payment.html"

    def get_form_class(self):
        return self.payment_provider.form_class

    def dispatch(self, request, *args, **kwargs):
        if not self.check():
            return HttpResponseRedirect(self.get_checkfailed_url())
        order = self.get_order()
        source = self.get_payment_source()
        status = order.status
        total = order.total_excl_tax
        if status == Order.STATUS_PENDING:
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
        if order.status in (Order.STATUS_PAID, Order.STATUS_FAILED):
            self.reset_session()
            return redirect('checkout:order', order.number)
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
        self.add_payment_source(order.sources.first().source_type)
        return redirect('checkout:payment')


class OrderDetailView(CheckoutSessionMixin, DetailView):
    model = get_model('order', 'Order')
    template_name = 'oparts/checkout/order_detail.html'
    slug_field = 'number' 
    slug_url_kwarg = 'number'
    checks = []
    checkout_urls = []

    def dispatch(self, request, *args, **kwargs):
        return (super(OrderDetailView, self)
                .dispatch(request, *args, **kwargs))

    def get_context_data(self, **kwargs):
        kwargs = super(OrderDetailView, self).get_context_data(**kwargs)
        user_is_auth = self.request.user.is_authenticated()
        try:
            placed_order = self.get_placed_order()
            order = self.get_object()
            if placed_order == order:
                kwargs.update(order_placed=True)
            elif not user_is_auth or order.user != self.request.user:
                raise PermissionDenied
        except Order.DoesNotExist:
            if not user_is_auth:
                raise PermissionDenied
        return kwargs


class YandexMoneyError(Exception):

    def __init__(self, code, message='yandex payment error', data={}):
        self.code = code
        self.message = message
        self.data = data
        self.data.update(message=message)

    def __str__(self): 
        return self.message


class YandexMoneyResponseView(TemplateResponseMixin, View):
    template_name = "oparts/checkout/yandex_money.xml"
    content_type = 'application/xml'
    tagname = 'base'
    http_method_names = ['post']


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        post = self.request.POST
        ctx= dict(
            tagname=self.tagname,
            invoice_id=post.get('invoiceId'),
            shop_id=post.get('shopId'))
        provider_code = 'yandex_kassa'
        payment_provider = providers_pool.get_by_code(provider_code)
        source_type_code = post.get('paymentType', '')
        order_number = post.get('orderNumber', '')
        action = post.get('action')
        md5 = post.get('md5')
        order_sum_amount = D(post.get('orderSumAmount', 0))
        shop_sum_amount = D(post.get('shopSumAmount', 0))
        try:
            order = Order.objects.filter(number=order_number).first()
            if not order:
                raise YandexMoneyError(code=100,
                        message=_('Invalid order number'))
            source = order.sources.filter(
                source_type__code=source_type_code,
                source_type__provider__code=provider_code
            ).first()
            if not source or not payment_provider:
                raise YandexMoneyError(code=100,
                        message=_('This payment type is not supported'))
            md5_kwargs = dict(
                action=post.get('action'),
                orderSumAmount=post.get('orderSumAmount'),
                orderSumCurrencyPaycash=post.get('orderSumCurrencyPaycash'),
                orderSumBankPaycash=post.get('orderSumBankPaycash'),
                shopId=payment_provider.settings.get('shopId'),
                invoiceId=post.get('invoiceId'),
                customerNumber=post.get('customerNumber'),
                shopPassword=payment_provider.settings['shopPassword'])
            check_md5 = yandex_money_checksum(**md5_kwargs)
            if md5 != check_md5:
                raise YandexMoneyError(code=1, data={
                    'post': post, 'md5': check_md5, 'md5_kwargs': md5_kwargs})
        except YandexMoneyError as error:
            if order:
                order.status = Order.STATUS_FAILED
                order.save()
            ctx.update(message=error.message, code=error.code)
            send_email_to_admins(request, 'YAMONEY_CHECK_DEBUG', error.data)
        else:
            ctx.update(code=0)
            if action == 'checkOrder':
                source.allocate(order_sum_amount)
                ctx.update(order_sum_amount=str(order_sum_amount))
            elif action == 'paymentAviso':
                source.debit(order_sum_amount)
            send_email_to_admins(request, 'YAMONEY_CHECK_DEBUG', ctx)
        context =  RequestContext(request, ctx) 
        return self.render_to_response(context)


class YandexMoneyCheckView(YandexMoneyResponseView):
    tagname = 'checkOrderResponse'


class YandexMoneyAvisoView(YandexMoneyResponseView):
    tagname = 'paymentAvisoResponse'


class YandexMoneyTestView(CheckoutSessionMixin, TemplateView):
    template_name = 'oparts/checkout/yandex_money_test.html'
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
            orderSumAmount=order.total_excl_tax,
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
            shopSumAmount=order.total_excl_tax,
            paymentType=source.source_type.code,
            md5=yandex_money_checksum(**md5_data)
        )
        site = get_current_site(self.request)
        if action == 'paymentAviso':
            data.update(
                paymentDatetime=request_datetime,
                cps_user_country_code='RU')
            url = reverse('checkout:yandex_money_aviso')
        else:
            url = reverse('checkout:yandex_money_check')
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