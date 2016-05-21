from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text
from django.utils.html import format_html

from oscar.core.loading import get_model
from oscar.core.utils import slugify

from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, USER_SETTINGS_BREAK
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar.items import LinkItem, SubMenu, URL_CHANGE
CommunicationEventType = get_model('customer', 'CommunicationEventType')


@toolbar_pool.register
class DashboardToolbar(CMSToolbar):

    def create_dashboard_menu(self, menu_items, parent=None):
        nodes = []
        view_name = self.request.resolver_match.view_name
        section_name = view_name.split(':dashboard_')[-1]
        for menu_dict in menu_items:
            try:
                label = menu_dict['label']
                icon=menu_dict.get('icon', None)
                if icon:
                    label = format_html(
                            smart_text(
                                '<small class="{icon}"></small> {label}'),
                            icon=icon, label=label)

                name = slugify(label)
            except KeyError:
                raise ImproperlyConfigured(
                    "No label specified for menu item in dashboard")
            children = menu_dict.get('children', [])
            if children:
                if not parent:
                    node = self.toolbar.get_or_create_menu(
                            'oscar_%s' % name, label)
                else:
                    node = SubMenu(label, parent.csrf_token, URL_CHANGE)
                self.create_dashboard_menu(children, parent=node)
            else:
                url_name=menu_dict.get('url_name', None)
                url_kwargs=menu_dict.get('url_kwargs', None)
                url_args=menu_dict.get('url_args', None)
                url = reverse(url_name, args=url_args, kwargs=url_kwargs) 
                active = (view_name == url_name)
                if not active:
                    active = (section_name == 
                            url_name.split(':dashboard_')[-1])
                node = LinkItem(label, url, active=active)
            if parent:
                parent.add_item(node)
                if node.active:
                    parent.name= format_html(
                            smart_text('<b>{}</b>'), parent.name)
            else:
                nodes.append(node)
        return nodes

    def populate(self):
        menu_items = settings.OSCAR_DASHBOARD_NAVIGATION
        url = reverse('dashboard:index')
        nodes = [LinkItem(_('Dashboard'), url, 
            active = (url==self.request.resolver_match.view_name) )]
        nodes += self.create_dashboard_menu(menu_items)
        return nodes
