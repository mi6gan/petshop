from petshop.core.views import AjaxFormMixin
from django.core.mail import mail_managers
from django.template.loader import select_template
from django.template.context import Context
from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponse
from django.forms.forms import pretty_name


class AjaxFeedbackView(AjaxFormMixin, FormView):
    form_slug = 'default'

    def get_mail_context_data(self, form):
        self._mail_context_data = getattr(self, '_mail_context_data',
                   {'data':[ { 'label': form.fields[k].label or pretty_name(k), 'value': v }
                     for k, v in form.cleaned_data.items() ] })
        return self._mail_context_data

    def get_mail_kwargs(self, form):
        if not getattr(self, '_mail_kwargs', None):
            ctx = Context(self.get_mail_context_data(form))
            form_slugs = [self.form_slug, 'default']
            self._mail_kwargs = {
                'subject': ''.join(select_template(['djangocms_feedback/%s_subject.txt' % s\
                    for s in form_slugs]).render(ctx).splitlines()),
                'message': select_template(['djangocms_feedback/%s_mail.txt' % s\
                    for s in form_slugs]).render(ctx),
                'html_message': select_template(['djangocms_feedback/%s_mail.html' % s\
                    for s in form_slugs]).render(ctx) 
            }
        return self._mail_kwargs

    def get_response_dict(self, form, **kwargs):
        kwargs.update({
            'message': unicode(_('Message is sent successfully.\n'
                               ' Our manager will contact you soon'))
        })
        return super(AjaxFeedbackView, self).get_response_dict(form, **kwargs)

    def form_valid(self, form):
        mail_managers(fail_silently=True, **self.get_mail_kwargs(form))
        return super(AjaxFeedbackView, self).form_valid(form)
