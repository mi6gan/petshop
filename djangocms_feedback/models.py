from django.db import models
from django.utils.translation import ugettext as _

from cms.models.pluginmodel import CMSPlugin

from . import FeedbackFormsManager


class FeedbackFormPluginModel(CMSPlugin):
	title=models.CharField(_('title'), max_length=128, null=True, blank=True)
	feedback_type=models.PositiveIntegerField(_('type'), choices=
		[(i, f.label) for i, f in enumerate(FeedbackFormsManager.objects())],
		null=True
	)
