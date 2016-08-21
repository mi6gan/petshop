from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import PageSitemapNode, CategorySitemapNode


class PageSitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('page', 'include')


class CategorySitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('category', 'include')


admin.site.register(PageSitemapNode, PageSitemapNodeAdmin)
admin.site.register(CategorySitemapNode, CategorySitemapNodeAdmin)
