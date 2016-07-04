from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from oscar.apps.payment.abstract_models import AbstractSourceType
from oscar.models.fields import AutoSlugField

from easy_thumbnails.fields import ThumbnailerImageField

from jsonfield import JSONField


class Provider(models.Model):
    name = models.CharField(max_length=128)
    code = models.SlugField(max_length=128, editable=False)
    site = models.ForeignKey(Site)
    settings = JSONField(null=True, editable=False)
    enabled = models.BooleanField(default=True)

    def get_absolute_url(self):
        pass

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code)

    def save(self, *args, **kwargs):
        super(Provider, self).save(*args, **kwargs)
        from .providers import providers_pool
        provider = providers_pool.get_by_code(self.code)
        provider.get_instance()

    class Meta:
        verbose_name = _('provider')
        verbose_name_plural = _('providers')


class SourceType(AbstractSourceType):
    provider = models.ForeignKey(Provider,
            related_name="source_types", null=True)
    icon = ThumbnailerImageField(verbose_name=_('icon'), 
                                 upload_to="oparts/payment",
                                 null=True, blank=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code)

    class Meta(AbstractSourceType.Meta):
        abstract = False


from oscar.apps.payment.models import *  # noqa
