from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from cmsplugin_filer_link.cms_plugins import FilerLinkPlugin

from django.forms.widgets import Media
from django.utils.translation import ugettext_lazy as _

from .models import CatalogueLinkPlugin, ProductsCarouselPlugin


class CatalogueLinkPlugin(FilerLinkPlugin):
    module = 'Filer'
    model = CatalogueLinkPlugin
    name = _("Link")
    text_enabled = True
    raw_id_fields = ('page_link', )
    render_template = "cmsplugin_filer_link/link.html"

    def render(self, context, instance, placeholder):
        if instance.product:
            instance.url = instance.product.get_absolute_url()
        elif instance.category:
            instance.url = instance.category.get_absolute_url()
        context = super(CatalogueLinkPlugin, self).render(
                context, instance, placeholder)
        return context


class ProductsCarouselPlugin(CMSPluginBase):

    name=_('Products carousel')
    model = ProductsCarouselPlugin
    
    def get_render_template(self, context, instance, placeholder):
        return ("catalogue/cmsplugin_products_carousel/%s_carousel.html" % 
                instance.style)

    def render(self, context, instance, placeholder):
        media = (
            Media(
                js=(
                    'vendor/js/bootstrap/carousel.js',
                ),
            )
        )
        context.update({
            'products': instance.get_products(),
            'title': instance.title,
            'media': media,
            'css_id': 'productsCarousel__%s' % instance.pk
        })
        return context


plugin_pool.register_plugin(ProductsCarouselPlugin)
plugin_pool.register_plugin(CatalogueLinkPlugin)
plugin_pool.unregister_plugin(FilerLinkPlugin)
