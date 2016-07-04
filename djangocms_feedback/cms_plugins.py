from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from . import FeedbackFormsManager
from .models import FeedbackFormPluginModel
from django.utils.module_loading import import_string
from django.template.loader import get_template
from django.template.base import TemplateDoesNotExist


class FeedbackFormPlugin(CMSPluginBase):
    name = _('Feedback form')
    model = FeedbackFormPluginModel 
    disable_child_plugins = True

    def get_render_template(self, context, instance, placeholder):
        feedback_type = FeedbackFormsManager.objects()[instance.feedback_type]
        try:
            template_name = "djangocms_feedback/%s_form.html" % feedback_type.slug
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            pass
        return 'djangocms_feedback/default_form.html'

    def render(self, context, instance, placeholder):
        feedback_type = FeedbackFormsManager.objects()[instance.feedback_type]
        view_class = feedback_type.view_class
        form_class = feedback_type.form_class
        
        view = feedback_type.view_class(request=context['request'], form_class=form_class)
        context.update({
            'form': view.get_form(form_class),
            'url': reverse_lazy(feedback_type.slug),
            'slug': feedback_type.slug,
            'instance': instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(FeedbackFormPlugin)
