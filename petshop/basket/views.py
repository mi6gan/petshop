from django.core.exceptions import NON_FIELD_ERRORS
from django.http.response import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView

from extra_views import ModelFormSetView

from oscar.core.loading import get_class, get_model

from petshop.core.views import AjaxFormMixin
from petshop.core.forms import combinedform_factory
from petshop.checkout.forms import CheckoutForm

from collections import OrderedDict

from .forms import (BasketLineForm, BasketLineFormSet,
                    MiniBasketLineFormSet, MiniBasketLineForm)


BasketAddView = get_class('basket.views', 'BasketAddView')
BasketView = get_class('basket.views', 'BasketView')
Applicator = get_class('offer.utils', 'Applicator')
Repository = get_class('shipping.repository', 'Repository')



class AjaxBasketAddView(AjaxFormMixin, BasketAddView):

    def form_valid(self, form):
        offers_before = self.request.basket.applied_offers()
        self.request.basket.add_product(
            form.product, form.cleaned_data['quantity'],
            form.cleaned_options())
        lines = form.basket.lines
        basket = form.basket
        formset = MiniBasketLineFormSet(strategy=self.request.strategy,
                                        queryset=lines.all())
        ctx = RequestContext(self.request, 
                             dict(basket=form.basket, formset=formset))
        content = render_to_string("basket/mini_basket.html", ctx)
        response = dict(content=content, result='ok')
        return JsonResponse(response)


class AjaxBasketView(BasketView):
    formset_class = MiniBasketLineFormSet
    form_class = MiniBasketLineForm
    http_method_names = ['post']
    template_name = 'basket/mini_basket.html'

    def get_ajax_response(self, context):
        content = render_to_string(self.template_name, context)
        response = dict(content=content, result='ok')
        return JsonResponse(response)

    def formset_invalid(self, formset):
        errors = {}
        for form in formset: 
            if form.non_field_errors():
                errors.update({NON_FIELD_ERRORS: form.non_field_errors()}) 
            for field_name in form.fields:
                field = form[field_name]
                if field.errors:
                    errors[field.html_name] = field.errors
        response = dict(errors=errors, result='error')
        return JsonResponse(response)

    def formset_valid(self, formset):
        offers_before = self.request.basket.applied_offers()
        response = super(BasketView, self).formset_valid(formset)
        basket = self.request.basket
        basket.strategy = self.request.strategy
        Applicator().apply(basket, self.request.user, self.request)
        offers_after = self.request.basket.applied_offers()
        kwargs = self.get_formset_kwargs()
        del kwargs['data']
        del kwargs['files']
        if 'queryset' in kwargs:
            del kwargs['queryset']
        formset = self.get_formset()(queryset=self.get_queryset(),
                                     **kwargs)
        ctx = self.get_context_data(formset=formset,
                                    basket=basket)
        context = RequestContext(self.request, ctx) 
        return self.get_ajax_response(context)


class BasketSummaryView(AjaxBasketView):
    form_class = BasketLineForm
    formset_class = BasketLineFormSet
    http_method_names = ['post', 'get']
    template_name = 'basket/summary.html'
    ajax_template_name = 'basket/partials/summary.html'
    extra = 0
    can_delete = True

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return (super(BasketSummaryView, self)
                .dispatch(request, *args, **kwargs))

    def get_ajax_response(self, context):
        content = render_to_string(self.ajax_template_name, context)
        response = dict(content=content, result='ok')
        return JsonResponse(response)

    def get_context_data(self, **kwargs):
        ctx = super(BasketSummaryView, self).get_context_data(**kwargs) 
        repo = Repository()

        ctx.update({
            'hide_mini_basket': True
        })

        basket = self.request.basket
        shipping_method = repo.get_current_shipping_method(self.request)
        if not shipping_method:
            shipping_method = repo.get_available_shipping_methods(basket)[0]
        checkout_form = CheckoutForm(basket, shipping_method)
        ctx.update(dict(checkout_form=checkout_form))
        return ctx
