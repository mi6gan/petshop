

class SitemapNodeMiddleware(object):

    def process_template_response(self, request, response):
        ctx = getattr(response, 'context_data', None)
        if ctx:
            node = None
            for varname in 'category', 'current_page':
                value = ctx.get(varname)
                if isinstance(value, object):
                    node = getattr(value, 'sitemap_node', None)
                if node:
                    break
            ctx['sitemap_node'] = node
            print node
        return response
