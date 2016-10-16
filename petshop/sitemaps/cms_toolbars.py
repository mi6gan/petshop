from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text
from django.utils.html import format_html

from oscar.core.loading import get_model
from oscar.core.utils import slugify

from cms.cms_toolbars import (
        ADMIN_MENU_IDENTIFIER, USER_SETTINGS_BREAK, PAGE_MENU_IDENTIFIER)
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar.items import LinkItem, SubMenu, URL_CHANGE


@toolbar_pool.register
class SEOToolbar(CMSToolbar):

    def populate(self):
        sitemap_node = self.request.sitemap_node
        if sitemap_node:
            url = sitemap_node.get_edit_url()
            if url:
                menu = self.toolbar.get_or_create_menu(
                            PAGE_MENU_IDENTIFIER, _('Page'))
                menu.add_sideframe_item('SEO', url)
