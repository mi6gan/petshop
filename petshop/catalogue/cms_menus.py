from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from cms.menu_bases import CMSAttachMenu
from cms.utils.page_resolver import get_page_queryset
from menus.base import NavigationNode, Modifier

from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from oscar.core.loading import get_model


class CatalogueMenu(CMSAttachMenu):
    name = _("Catalogue")

    def get_nodes(self, request):
        Category = get_model('catalogue', 'Category')
        ProductCategory = get_model('catalogue', 'ProductCategory')
        nodes = []
        for category in Category.objects.all():
            if category.depth > 1:
                parent_id = category.get_parent().pk
            else:
                parent_id = None
            node =  NavigationNode(
                title=category.name,
                url=category.get_absolute_url(),
                id=category.pk,
                parent_id=parent_id
            )
            node.attr["is_category"] = True
            nodes.append(node)
            for product_category in (
                    ProductCategory.objects.filter(category=category)):
                product = product_category.product
                node = NavigationNode(
                    title=product.title,
                    url=product.get_absolute_url(),
                    id=product_category.pk,
                    parent_id=category.pk,
                    visible=False
                )
                node.attr["is_product"] = True
                nodes.append(node)
        return nodes


menu_pool.register_menu(CatalogueMenu)
