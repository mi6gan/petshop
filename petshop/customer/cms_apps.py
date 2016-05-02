from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class

from .cms_menus import CustomerMenu


app = get_class('customer.app', 'application')


class CustomerApp(CMSApp):
    name = _("Customer profile")
    app_name = app.name
    menus = [CustomerMenu]
    urls = [app.get_urls()]
    permissions = False


apphook_pool.register(CustomerApp)
