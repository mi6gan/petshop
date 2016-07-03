from django.db import models

from cms.models import Page

from .abstract_models import SitemapNode


class PageSitemapNode(SitemapNode):

    page = models.OneToOneField(Page, related_name='sitemap_node')

    @property
    def has_changes(self):
        return self.page.changed_date > self.lastmod
