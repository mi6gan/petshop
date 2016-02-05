from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from easy_thumbnails.fields import ThumbnailerImageField


class SiteSettings(models.Model):

    class Meta:
        verbose_name = _('Site settings')
        verbose_name_plural = _('Site settings')


    site = models.OneToOneField(Site, editable=False, related_name='settings')

    logo = ThumbnailerImageField(
            verbose_name=_('logo'), upload_to="petshop/logo")

    favicon = ThumbnailerImageField(
            verbose_name=_('favicon'), upload_to="petshop/favicon")

    def __str__(self):
        return self.site.name

    @classmethod
    def get_current(cls):
        return cls.objects.get_or_create(
                    site=Site.objects.get_current())[0]
