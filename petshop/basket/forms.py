from django.forms.models import modelformset_factory
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django import forms

from oscar.core.loading import get_class, get_model
from oscar.forms.widgets import AdvancedSelect
from oscar.templatetags.currency_filters import currency
from oscar.apps.basket.forms import (
        AddToBasketForm as OscarAddToBasketForm,
        BaseBasketLineFormSet as OscarBaseBasketLineFormSet,
        BasketLineForm as OscarBasketLineForm)

from petshop.core.forms import (
        Form, ModelForm, ButtonInput, StyledCheckboxInput)

Line = get_model('basket', 'Line')


class MiniBasketLineForm(ModelForm):

    class Media:
        js = ('vendor/js/bootstrap/button.js',
              'vendor/js/bootstrap/collapse.js',
              'vendor/js/bootstrap/transition.js',
              'vendor/js/bootstrap/tooltip.js',
              'vendor/js/bootstrap/popover.js',
              'js/forms/mini.basket.js')
        css = {
            'all': ('css/mini.basket.css',)
        }

    class Meta:
        model = Line
        fields = []

    def __init__(self, strategy=None, *args, **kwargs):
        super(MiniBasketLineForm, self).__init__(*args, **kwargs)
        self.instance.strategy = strategy


class BaseMiniBasketLineFormSet(forms.BaseModelFormSet):
    form = MiniBasketLineForm

    def __init__(self, strategy, *args, **kwargs):
        self.strategy = strategy
        super(BaseMiniBasketLineFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        return super(BaseMiniBasketLineFormSet, self)._construct_form(
                                    i, strategy=self.strategy, **kwargs)

    def add_fields(self, form, index):
        super(BaseMiniBasketLineFormSet, self).add_fields(form, index)
        label_attrs = {
            'class': 'fa fa-remove'
        }
        button_attrs = {
            'class': 'btn-link',
            'title': _('Remove from basket')
        }
        label = mark_safe(format_html("<span{}></span>", flatatt(label_attrs)))
        form.fields[DELETION_FIELD_NAME].widget = (
                ButtonInput(label=label, attrs=button_attrs))
        form.fields[DELETION_FIELD_NAME].initial = True


MiniBasketLineFormSet = modelformset_factory(
    Line, form=MiniBasketLineForm, formset=BaseMiniBasketLineFormSet,
    extra=0, can_delete=True)


class BasketLineForm(ModelForm, OscarBasketLineForm):

    class Meta:
        model = Line
        fields = ['quantity']
    quantity = forms.IntegerField(
            min_value = 1,
            widget=forms.NumberInput(attrs={'data-submitonchange': True}))

    def __init__(self, strategy, *args, **kwargs):
        super(BasketLineForm, self).__init__(strategy, *args, **kwargs)
        self.instance.basket.strategy = strategy


class BaseBasketLineFormSet(OscarBaseBasketLineFormSet):

    def add_fields(self, form, index):
        super(BaseBasketLineFormSet, self).add_fields(form, index)
        label_attrs = {
            'class': 'fa fa-remove'
        }
        button_attrs = {
            'class': 'btn-link',
            'title': _('Remove from basket')
        }
        label = mark_safe(format_html("<i{}></i>", flatatt(label_attrs)))
        form.fields[DELETION_FIELD_NAME].widget = (
                ButtonInput(label=label, attrs=button_attrs))
        form.fields[DELETION_FIELD_NAME].initial = True

    @property
    def empty_form(self):
        form = self.form(
            strategy = None,
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
        )
        self.add_fields(form, None)
        return form


class ParentProductSelect(AdvancedSelect):
    
    def __init__(self, attrs=None, choices=(), disabled_values=(),
                 choices_extra={}):
        self.disabled_values = set(force_text(v) for v in disabled_values)
        self.choices_extra = choices_extra
        super(ParentProductSelect, self).__init__(attrs, choices)

    def render_option(self, selected_choices, option_value, option_label):
        extra_attrs = self.choices_extra.get(option_value, {})
        option_value = force_text(option_value)
        if option_value in self.disabled_values:
            selected_html = mark_safe(' disabled="disabled"')
        elif option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html(u'<option value="{0}"{1}{2}>{3}</option>',
                           option_value,
                           selected_html,
                           flatatt(extra_attrs),
                           force_text(option_label))


class AddToBasketForm(OscarAddToBasketForm):

    class Media:
        js = ('js/forms/add.to.basket.js',)

    def __init__(self, basket, product, *args, **kwargs):
        super(AddToBasketForm, self).__init__(
                basket, product, *args, **kwargs)

    def _add_option_field(self, product, option):
        """
        Creates the appropriate form field for the product option.

        This is designed to be overridden so that specific widgets can be used
        for certain types of options.
        """
        kwargs = {'required': option.is_required}
        self.fields[option.code] = forms.CharField(**kwargs)

    def _create_parent_product_fields(self, product):
        """
        Adds the fields for a "group"-type product (eg, a parent product with a
        list of children.

        Currently requires that a stock record exists for the children
        """
        choices = []
        disabled_values = []
        choices_extra = {}
        for child in product.children.all():
            # Build a description of the child, including any pertinent
            # attributes
            attr_summary = child.attribute_summary
            if attr_summary:
                summary = attr_summary
            else:
                summary = child.get_title()

            # Check if it is available to buy
            info = self.basket.strategy.fetch_for_product(child)
            if not info.availability.is_available_to_buy:
                disabled_values.append(child.id)
            else:
                price = (info.price.incl_tax 
                        if info.price.is_tax_known else info.price.excl_tax)
                choices_extra[child.id] = {
                    'data-price': currency(price, info.price.currency)
                }
            choices.append((child.id, summary))
        self.fields['child_id'] = forms.ChoiceField(
            choices=tuple(choices), label=_("Variant"),
            widget=ParentProductSelect(disabled_values=disabled_values,
                                       choices_extra=choices_extra))

class SimpleAddToBasketForm(AddToBasketForm):
    quantity = forms.IntegerField(
        initial=1, min_value=1, widget=forms.HiddenInput, label=_('Quantity'))



BasketLineFormSet = modelformset_factory(
    Line, form=BasketLineForm, formset=BaseBasketLineFormSet,
    extra=0, can_delete=True)
