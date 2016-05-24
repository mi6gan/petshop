from django import template
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.forms.utils import flatatt
from django.http.request import QueryDict
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import six

register = template.Library()

def render_pagination_page(page, page_obj, url):
    if page is page_obj.number:
        li_attrs = {'class': 'active'}
    else:
        li_attrs = {}
    if page is 1:
        a_attrs = {'href': url}
    else:
        a_attrs = {
            'href': '%s?page=%s' % (url, page)
        }
    return format_html(
            u'<li{}><a{}>{}</a></li>\n',
            flatatt(li_attrs), flatatt(a_attrs), page)

@register.simple_tag
def render_pagination(
        paginator, page_obj, url='', extra_pages=4, css_class="pagination"):
    num_pages = paginator.num_pages
    page_range = paginator.page_range
    if num_pages <= 1:
        return ''
    cache_key = '%s_%s_%s' % (url, num_pages, page_obj.number)
    cached = cache.get(cache_key, False)
    if cached:
        return cached
    page_from = page_obj.number - 1 - extra_pages
    page_to = page_obj.number + extra_pages
    if page_from < 0:
        page_to = page_to + abs(page_from) + 1 
        page_from = 0
    if page_obj.number - page_from < extra_pages:
        page_to = page_to + (page_obj.number - page_from - extra_pages)
    if page_to > num_pages:
        page_from = page_from + (num_pages-page_to) 
        page_to = num_pages 
        if page_from < 0:
            page_from = 0
    pages = page_range[page_from:page_obj.number]
    pages += page_range[page_obj.number:page_to]
    items = []
    for page in pages:
        if page is page_from + 1:
            if page != 1:
                item = render_pagination_page(
                        1, page_obj, url)
                items.append(item)
            if page > 2:
                item = u'<li><a>...</a></li>'
                items.append(item)
        item = render_pagination_page(
                page, page_obj, url) 
        items.append(item)
        if page is page_to:
            if page < num_pages - 2:
                item = u'<li><a>...</a></li>'
                items.append(item)
            if page != num_pages:
                item = render_pagination_page(
                        num_pages, page_obj,
                        url)
                items.append(item)
    ul_attrs = {'class': css_class}
    cached = mark_safe(format_html(
        u'<ul{}>{}</ul>', flatatt(ul_attrs), mark_safe('\n'.join(items))))
    cache.set(cache_key, cached)
    return cached
