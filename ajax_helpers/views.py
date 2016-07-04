from django.http.response import JsonResponse
from django.views.generic.edit import FormMixin

import six


class AjaxFormMixin(FormMixin):
    success_url = './'

    def form_errors_dict(self,form):
        field_errors=filter(
            lambda a: a,
            [
                (name,form[name].errors)
                if form[name].errors else () 
                for name,field in form.fields.items()
            ]
        )
        return {
            'field_errors': list(field_errors),
            'non_field_errors': form.non_field_errors(),
            'result': 'error'
        }

    def form_invalid(self, form):
        errors = self.form_errors_dict(form)
        return JsonResponse(errors,status=412)

    def form_valid(self, form):
        response_dict = self.get_response_dict(form)
        return JsonResponse(response_dict)

    def get_response_dict(self, form, **kwargs):
        self.success_url = self.get_success_url()
        if not isinstance(self.success_url, six.string_types):
            self.success_url = form.cleaned_data.get('success_url')
        kwargs.update({'success_url': self.success_url, 'result': 'ok'})
        return kwargs


class AjaxModelFormMixin(AjaxFormMixin):

    def form_valid(self, form):
        self.object = form.save()
        return super(AjaxModelFormMixin, self).form_valid(form)
