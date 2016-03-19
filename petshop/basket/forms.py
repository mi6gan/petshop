from django.forms.models import modelformset_factory
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django import forms

from oscar.core.loading import get_class, get_model
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


BasketLineFormSet = modelformset_factory(
    Line, form=BasketLineForm, formset=BaseBasketLineFormSet,
    extra=0, can_delete=True)
