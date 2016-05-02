from cms.menu_bases import CMSAttachMenu

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool


class CustomerMenu(CMSAttachMenu):
    name = _("Customer")

    def get_nodes(self, request):
        items = ( 
            (reverse('customer:order-list'), _("Order History")),
            (reverse('customer:address-list'), _("Address Book")),
            (reverse('customer:email-list'), _("Email History")),
            (reverse('customer:alerts-list'), _("Product Alerts")),
            (reverse('customer:notifications-inbox'), _("Notifications")),
        )
        nodes = []
        for _id, (url, title) in enumerate(items, 1):
            nodes.append(
                NavigationNode(title, url, _id))
        return nodes


menu_pool.register_menu(CustomerMenu)
