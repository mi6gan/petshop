from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from cms.models import Page
from oscar.core.loading import get_model

from .abstract_models import SitemapNode


Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')


@python_2_unicode_compatible
class PageSitemapNode(SitemapNode):

    page = models.OneToOneField(
            Page, verbose_name=_('Page'), related_name='sitemap_node')
    meta_keywords = models.TextField(max_length=100, blank=True, null=True)

    @property
    def page_title(self):
        title = self.page.title_set.first()
        if title:
            return title.page_title

    @property
    def meta_description(self):
        title = self.page.title_set.first()
        if title:
            return title.meta_description

    @property
    def has_changes(self):
        return self.page.changed_date > self.lastmod

    def __str__(self):
        return self.page.get_title()

    class Meta:
        verbose_name = (_('CMS page SEO options'))
        verbose_name_plural = (_('CMS page SEO options'))


@python_2_unicode_compatible
class CategorySitemapNode(SitemapNode):

    category = models.OneToOneField(
            Category, verbose_name=_('Category'), related_name='sitemap_node')

    @property
    def page_title(self):
        return self.category.page_title

    @property
    def meta_description(self):
        return self.category.meta_description

    @property
    def meta_keywords(self):
        return self.category.meta_keywords

    @property
    def has_changes(self):
        product= (Product.objects.filter(categories=self.category)
                    .distinct().order_by('-date_updated').first())
        return (product and product.date_updated > self.lastmod)

    def __str__(self):
        return self.category.name

    class Meta:
        verbose_name = (_('catalogue category SEO options'))
        verbose_name_plural = (_('catalogue category SEO options'))


@python_2_unicode_compatible
class CustomSitemapNode(SitemapNode):

    has_changes = True

    def __str__(self):
        return self.location

    class Meta:
        verbose_name = (_('custom SEO entry'))
        verbose_name_plural = (_('custom SEO entries'))
        ordering = ['location']
