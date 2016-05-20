from django import forms
from django.conf import settings
from django.forms.forms import BaseForm as DjangoBaseForm
from django.forms.widgets import (ChoiceFieldRenderer,
                                  RadioChoiceInput)
from django.forms.forms import (DeclarativeFieldsMetaclass,
                                BaseForm as DjangoBaseForm)
from django.forms.widgets import Input
from django.forms.models import (ModelFormMetaclass as
                                    DjangoModelFormMetaclass,
                                 BaseModelForm)
from django.utils.translation import ugettext_lazy as _
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.encoding import force_text

from collections import OrderedDict
import six
import inspect


class BaseForm(DjangoBaseForm):

    class Media:
        js = ('vendor/js/bootstrap/button.js',
              'vendor/js/bootstrap/transition.js',
              'vendor/js/bootstrap/tooltip.js',
              'vendor/js/bootstrap/popover.js',
              'js/forms/base.js',)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        for k, field in self.fields.items():
            if not hasattr(self, '_meta') or not self._meta.error_messages\
                    or k.split('-')[-1] not in self._meta.error_messages:
                field.error_messages['required'] = _('This field can\'t be empty')
            cls = field.widget.attrs.get('class', '')
            input_type = getattr(field.widget, 'input_type', '')
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                field.widget.attrs['class'] = (
                    ' '.join(cls.split(' ') + ['form-control',]))
            BaseForm.wrap_field_clean(field)

    @staticmethod
    def wrap_field_clean(field):
        field_wrapped_clean = field.clean
        def field_clean(value, initial=None):
            if isinstance(value, six.string_types):
                value = value.strip()
            if initial:
                cleaned = field_wrapped_clean(value, initial)
            else:
                cleaned = field_wrapped_clean(value)
            return cleaned
        field.clean = field_clean


class Form(six.with_metaclass(DeclarativeFieldsMetaclass, BaseForm)):
    pass


class ModelFormMetaclass(DjangoModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        if not BaseForm in bases:
            bases = bases + (BaseForm,)
        return (
            super(ModelFormMetaclass, mcs).__new__(mcs, name, bases, attrs))


class ModelForm(six.with_metaclass(ModelFormMetaclass, BaseModelForm)):
    pass


class InputWithSubmit(forms.TextInput):

    def __init__(self, attrs=None, icon='ok'):
        super(InputWithSubmit, self).__init__(attrs)
        self.icon = icon

    def render(self, name, value, attrs=None):
        input_html = super(InputWithSubmit, self).render(name, value, attrs)
        group_attrs = {
            'class': 'input-group'
        }
        group_btn_attrs = {
            'class': 'input-group-btn'
        }
        button_attrs = {
            'class': 'btn btn-primary',
            'type': 'submit'
        }
        icon_attrs = {
            'class': 'glyphicon glyphicon-%s' % self.icon
        }
        return format_html(u'<div{}>{}<div{}><button{}><span{}>'
                           u'</span></button></div></div>',
                           flatatt(group_attrs),
                           input_html,
                           flatatt(group_btn_attrs),
                           flatatt(button_attrs),
                           flatatt(icon_attrs))


class ButtonInput(Input):

    def __init__(self, attrs=None, label=''):
        super(ButtonInput, self).__init__(attrs)
        self.label = label

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type='submit', name=name)
        final_attrs['value'] = '1'
        return format_html(u'<button{0}>{1}</button>',
                           flatatt(final_attrs), self.label)

    def value_from_datadict(self, data, files, name):
        value = str(data.get(name, None))
        return value == '1'


class StyledCheckboxInput(forms.CheckboxInput):

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs.update({'class': 'styled'})
        input_html = super(
                StyledCheckboxInput, self).render(name, value, attrs)
        return format_html('{}<span></span>', input_html)


class StyledRadioChoiceInput(RadioChoiceInput):

    def tag(self, attrs=None):
        attrs = attrs or {}
        attrs.update({'class': 'styled'})
        input_html = super(
                StyledRadioChoiceInput, self).tag(attrs)
        return format_html(u'{}<span></span>', input_html)

    def render(self, name=None, value=None, attrs=None, choices=()):
        if self.id_for_label:
            label_for = format_html(' for="{}"', self.id_for_label)
        else:
            label_for = ''
        attrs = dict(self.attrs, **attrs) if attrs else self.attrs
        return format_html(u'<label{0}><span>{2}</span> {1}</label>', label_for,
                           self.choice_label, self.tag(attrs))
   

class PaymentRadioChoiceInput(StyledRadioChoiceInput):

    def render(self, name=None, value=None, attrs=None, choices=()):
        if self.id_for_label:
            label_for = format_html(' for="{}"', self.id_for_label)
        else:
            label_for = ''
        attrs = dict(self.attrs, **attrs) if attrs else self.attrs
        return format_html(
                u'<label{0}>{2}{1}<span></span></label>',
                label_for, self.choice_label, self.tag(attrs))


class StyledRadioSelect(forms.RadioSelect):
    renderer = type('FieldRenderer', (ChoiceFieldRenderer,),
                        {'choice_input_class': StyledRadioChoiceInput,
                         'outer_html': u'<ul{id_attr} class="list-unstyled">'
                                            u'{content}'
                                       u'</ul>',
                         'inner_html': 
                            u'<li>{sub_widgets}{choice_value}</li>'})


class PaymentRadioSelect(forms.RadioSelect):
    renderer = type('FieldRenderer', (StyledRadioSelect.renderer,),
                    {'choice_input_class': PaymentRadioChoiceInput})


class PhoneNumberMaskWidget(forms.TextInput):

    class Media:
        js = ('vendor/js/inputmask/inputmask.js',
              'vendor/js/inputmask/jquery.inputmask.js')

    def build_attrs(self, extra_attrs={}, **kwargs):
        extra_attrs.update({
            'data-inputmask': "'mask': '+7 (999) 999-9999'",
        })
        return (super(PhoneNumberMaskWidget, self)
               .build_attrs(extra_attrs, **kwargs))

    def render(self, name, value, attrs=None):
        if attrs:
            selector = u'#%s' % attrs.get('id')
        if not selector:
            selector = u':input'
        input_html = (super(PhoneNumberMaskWidget, self)
                .render(name, value, attrs))
        return format_html(u"{}<script>$(function(){{$('{}').inputmask()}});</script>",
                           input_html, selector)


class BaseCombinedForm(object):

    class SubFormWrapper(object):

        def __init__(self, form_class, prefix):
            self.fields = OrderedDict()
            self.form_class = form_class
            self.prefix = prefix
            for field_name, field in form_class.base_fields.items():
                new_field_name = '%s-%s' % (self.prefix, field_name)
                self.fields[field_name] = (new_field_name, field)

        def get_form(self, *args, **kwargs):
            kwargs['prefix'] = self.prefix
            return self.form_class(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        argspec = inspect.getargspec(DjangoBaseForm.__init__)
        base_kwargs_items = [(k,v) 
                              for k, v in kwargs.items() 
                              if k in argspec[0]]
        self.forms = []
        for subform in self.subforms:
            form = subform.get_form(
                    *args, 
                    **dict(base_kwargs_items + 
                           kwargs.pop('%s__kwargs' % subform.prefix, 
                                      {}).items()))
            self.forms.append(form)
            setattr(self, subform.prefix, form)
        super(BaseCombinedForm, self).__init__(*args, **kwargs)

    @classmethod
    def subform_prefix(cls, form_class):
        for subform in cls.subforms:
            if form_class is subform.form_class:
                return subform.prefix

    @property
    def media(self):
        media = sum((f.media for f in self.forms),
                    super(BaseCombinedForm, self).media)
        return media

    def _clean_fields(self):
        pass

    def full_clean(self):
        super(BaseCombinedForm, self).full_clean()
        for form in self.forms:
            form.full_clean()
            subclean = getattr(self, '%s_subclean' % form.prefix, False)
            if subclean:
                subclean(form)
            for f, e in form._errors.items():
                if f != '__all__':
                    self.add_error('%s-%s' % (form.prefix, f), e)
                else:
                    self.add_error(None, e)


def combinedform_factory(form_classes_tuple,
        base_form=BaseCombinedForm, name=None):
    attrs = {'subforms': []}
    opts = {}
    for form_name, form_class in form_classes_tuple:
        subform = BaseCombinedForm.SubFormWrapper(form_class, form_name)
        attrs.update(OrderedDict(subform.fields.values()))
        attrs['subforms'].append(subform)
        if hasattr(form_class, 'Meta'):
            opts.update(form_class._meta.__dict__) 
    if not name:
        name = "Combined%sForm" % ''.join(
                    form_class.__name__.strip('Form')
                    for __, form_class in form_classes_tuple)
    attrs['_meta'] = type('_meta', (), opts)
    new_class = type(Form)(name, (base_form, Form), attrs)
    return new_class
