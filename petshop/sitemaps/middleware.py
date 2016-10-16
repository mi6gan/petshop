from django.apps import apps

from .models import PageSitemapNode, CategorySitemapNode


class SitemapNodeMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        if match and match.app_name == 'catalogue':
            pk = view_kwargs.get('pk')
            if pk:
                Category = apps.get_model('catalogue', 'category')
                category = Category.objects.filter(pk=pk).first()
                if category:
                    request.sitemap_node, __ = (
                        CategorySitemapNode.objects.get_or_create(
                            category=category,
                            defaults={
                                'location': category.get_absolute_url()
                            }))
                    request.sitemap_node = category.sitemap_node
                    return
        current_page = getattr(request, 'current_page', None)
        if current_page:
            request.sitemap_node, __ = (
                PageSitemapNode.objects.get_or_create(
                    page=current_page,
                    location=current_page.get_absolute_url()))
            request.sitemap_node = current_page.sitemap_node

    def process_template_response(self, request, response):
        ctx = getattr(response, 'context_data', None)
        if ctx:
            sitemap_node = getattr(request, 'sitemap_node', None)
            if sitemap_node:
                ctx['sitemap_node'] = getattr(request, 'sitemap_node')
        return response
