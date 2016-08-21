from decimal import Decimal as D

from django.contrib.sitemaps import Sitemap

from django.db.models.signals import post_save
from django.dispatch import receiver

from .abstract_models import SitemapNode
from .models import Page, PageSitemapNode, Category, CategorySitemapNode


class PetshopSitemap(Sitemap):

    model = SitemapNode

    def items(self):
        return self.model.objects.exclude(
                location='/accounts/').exclude(include=False)

    def changefreq(self, obj):
        return obj.get_changefreq_display()

    def lastmod(self, obj):
        return obj.lastmod

    def location(self, obj):
        return obj.location

    def priority(self, obj):
        return obj.priority


class PageSitemap(PetshopSitemap):
    model = PageSitemapNode


class CategorySitemap(PetshopSitemap):
    model = CategorySitemapNode


sitemaps = {
    'page': PageSitemap,
    'category': CategorySitemap
}


@receiver(post_save, sender=Page)
def create_page_sitemap_node(instance, **kwargs):
    page = instance
    if page.publisher_is_draft:
        return
    node, __ = PageSitemapNode.get_or_update(page)
    if not node:
        node = PageSitemapNode(page=page, location=page.get_absolute_url())
        if page.is_home:
            node.priority = D('1.0')
            node.changefreq = SitemapNode.DAILY
        else:
            priority = (D('1.0') * (
                (D('4.0') - page.depth) / D('4.0'))).quantize(D('0.0'))
            if priority <= D('0.0'):
                return
            if priority >= D('0.8'):
                node.changefreq = SitemapNode.WEEKLY
            else:
                node.changefreq = SitemapNode.MONTHLY
            node.priority = priority
        node.save()


@receiver(post_save, sender=Category)
def create_category_sitemap_node(instance, **kwargs):
    category = instance
    node, __ = CategorySitemapNode.get_or_update(category)
    if not node:
        node = CategorySitemapNode(
                category=category, location=category.get_absolute_url())
        priority = (D('1.0') * (
                (D('4.0') - category.depth) / D('4.0'))).quantize(D('0.0'))
        if priority <= D('0.0'):
            return
        if priority >= D('0.8'):
            node.changefreq = SitemapNode.WEEKLY
        else:
            node.changefreq = SitemapNode.MONTHLY
        node.priority = priority
        node.save()
