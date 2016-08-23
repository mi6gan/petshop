

class SitemapNodeMiddleware(object):

    def process_template_response(self, request, response):
        ctx = getattr(response, 'context_data', None)
        if ctx:
            node = None
            for value in (ctx.get('category'),
                    getattr(request, 'current_page', None)):
                if value:
                    node = getattr(value, 'sitemap_node', None)
                if node:
                    break
            ctx['sitemap_node'] = node
        return response
