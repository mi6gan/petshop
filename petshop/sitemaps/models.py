from cms.models import Page
from cms.extensions.models import PageExtension

from .abstract_models import SitemapNode


class PageSitemapNode(SitemapNode, PageExtension):

    page = models.ForeignKey(
            Page, related_name='sitemap_node', unique=True)

    @property
    def page(self):
        return self.extended_object

    @property
    def has_changes(self):
        return self.page.changed_date > self.lastmod
