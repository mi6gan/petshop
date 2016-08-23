from menus.base import Modifier
from menus.menu_pool import menu_pool
from .models import CategorySitemapNode, PageSitemapNode

from cms.models import Page

class SitemapNodeModifier(Modifier):

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if post_cut:
            return nodes
        for node in nodes:
            if node.attr.get("is_page"):
                try:
                    node.attr["sitemap_included"] = (
                        PageSitemapNode.objects.get(page__id=node.id).include
                        )
                except PageSitemapNode.DoesNotExist:
                    pass
            elif node.attr.get("is_category"):
                try:
                    node.attr["sitemap_included"] = (
                        CategorySitemapNode.objects.get(
                            category__id=node.id).include)
                except CategorySitemapNode.DoesNotExist:
                    pass
        return nodes

menu_pool.register_modifier(SitemapNodeModifier)
