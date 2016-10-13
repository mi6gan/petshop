from django.apps import apps

class SitemapNodeMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        if match and match.app_name == 'catalogue':
            pk = view_kwargs.get('pk')
            if pk:
                Category = apps.get_model('catalogue', 'category')
                category = Category.objects.filter(pk=pk).first()
                if category:
                    request.sitemap_node = category.sitemap_node
                    return
        current_page = getattr(request, 'current_page', None)
        if current_page:
            request.sitemap_node = current_page.sitemap_node

    def process_template_response(self, request, response):
        ctx = response.context_data
        if ctx:
            sitemap_node = getattr(request, 'sitemap_node', None)
            if sitemap_node:
                ctx['sitemap_node'] = getattr(request, 'sitemap_node')
        return response
