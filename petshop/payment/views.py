from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from decimal import Decimal as D

from oscar.core.loading import get_model

from petshop.core.utils import send_email_to_admins, yandex_money_checksum

from .providers import providers_pool


Order = get_model('order', 'Order')


class YandexMoneyError(Exception):

    def __init__(self, code, message='yandex payment error', data={}):
        self.code = code
        self.message = message
        self.data = data
        self.data.update(message=message)

    def __str__(self): 
        return self.message


class YandexMoneyResponseView(TemplateResponseMixin, View):
    template_name = "payment/yandex_money.xml"
    content_type = 'application/xml'
    tagname = 'base'
    http_method_names = ['post']


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        post = request.POST
        ctx= dict(
            tagname=self.tagname,
            invoice_id=post.get('invoiceId'),
            shop_id=post.get('shopId'))
        provider_code = 'yandex_kassa'
        payment_provider = providers_pool.get_by_code(provider_code).instance
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
                ctx.update(order_sum_amount=str(order_sum_amount))
            elif action == 'paymentAviso':
                if source.amount_allocated >= source.amount_debited:
                    source.debit(order_sum_amount)
            send_email_to_admins(request, 'YAMONEY_CHECK_DEBUG', ctx)
        context =  RequestContext(request, ctx) 
        return self.render_to_response(context)


class YandexMoneyCheckView(YandexMoneyResponseView):
    tagname = 'checkOrderResponse'


class YandexMoneyAvisoView(YandexMoneyResponseView):
    tagname = 'paymentAvisoResponse'

class DefaultProviderView(View):
    pass
