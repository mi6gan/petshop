from django.contrib.sitemaps.views import sitemap

from .sitemaps import sitemaps

def petshop_sitemap(request):
    return sitemap(request, sitemaps, template_name='sitemaps/sitemap.xml')
