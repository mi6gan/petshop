'''
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import PageSitemapNode


class SitemapNodeInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance and instance.pk:
            kwargs.setdefault('initial', [{
                    'location': instance.get_absolute_url()
                }])
        super(SitemapNodeInlineFormSet, self).__init__(*args, **kwargs)


class PageSitemapNodeAdmin(PageExtensionAdmin):
    model = PageSitemapNode
    readonly_fields = ('lastmod',)
    formset = SitemapNodeInlineFormSet
    max_num = 1


admin.site.register(PageSitemapNode, PageSitemapNodeAdmin)
'''
