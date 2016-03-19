from django.core.exceptions import NON_FIELD_ERRORS
from django.http.response import JsonResponse
from django.views.generic.edit import FormMixin, FormView

import six


class AjaxFormMixin(FormMixin):
    success_url = './'

    def form_errors_dict(self,form):
        errors = {}
        if form.non_field_errors():
            errors.update({NON_FIELD_ERRORS: form.non_field_errors()}) 
        for field_name in form.fields:
            field = form[field_name]
            if field.errors:
                errors[field.html_name] = field.errors
        return errors

    def form_invalid(self, form):
        errors = self.form_errors_dict(form)
        return JsonResponse({'result': 'error', 'errors': errors})

    def form_valid(self, form):
        response_dict = self.get_response_dict(form)
        return JsonResponse(response_dict)

    def get_response_dict(self, form, **kwargs):
        self.success_url = self.get_success_url()
        if not isinstance(self.success_url, six.string_types):
            self.success_url = form.cleaned_data.get('success_url')
        kwargs.update({'result': 'ok', 'success_url': self.success_url})
        return kwargs


class AjaxModelFormMixin(AjaxFormMixin):

    def form_valid(self, form):
        self.object = form.save()
        return super(AjaxModelFormMixin, self).form_valid(form)


class AjaxFormView(AjaxFormMixin, FormView):
    pass
