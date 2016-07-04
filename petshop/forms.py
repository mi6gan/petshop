from django import forms
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField

import six

from .core.forms import Form, PhoneNumberMaskWidget


class FeedbackForm(Form):

    class Media:
        js = ('js/forms/base.js',)

    name = forms.CharField(label=_('Your name'))
    email = forms.EmailField(label=_('Your e-mail'), 
            widget=forms.TextInput, required=False)
    phone = PhoneNumberField(label=_('or phone number'),
            widget=PhoneNumberMaskWidget, required=False)
    message = forms.CharField(label=_('Your message'), 
            widget=forms.Textarea(attrs={'rows': 5}))


    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label

    def clean(self):
        custom_errors = {}
        for name, message in (('email', _('Provide your e-mail')),
                              ('phone', _('or phone number'))): 
                value = self.cleaned_data.get(name, '')
                if not value and name not in self.errors:
                    custom_errors[name] = message
        if len(custom_errors) > 1:
            for name, error in custom_errors.items():
                self.add_error(name, error)
        return self.cleaned_data
