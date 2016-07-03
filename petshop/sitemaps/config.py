from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SitemapsConfig(AppConfig):
    label = 'sitemaps'
    name = 'petshop.sitemaps'
    verbose_name = _('Petshop sitemaps')
