from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class

from .cms_menus import CatalogueMenu


app = get_class('catalogue.app', 'application')


class CatalogueApp(CMSApp):
    name = _("Catalogue")
    app_name = app.name
    menus = [CatalogueMenu]
    urls = [app.get_urls()]
    permissions = False


apphook_pool.register(CatalogueApp)
