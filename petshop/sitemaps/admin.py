from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from .models import PageSitemapNode, CategorySitemapNode, CustomSitemapNode


class SitemapNodeForm(forms.ModelForm):
    page_title = forms.CharField(label=_('title'), required=False)
    meta_description = forms.CharField(label=_('description'), required=False)
    meta_keywords = forms.CharField(label=_('keywords'), required=False)


class PageSitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('page', 'include')
    fields = ('page', 'page_title', 'meta_description', 'meta_keywords',
              'changefreq', 'lastmod', 'location', 'priority', 'include')
    readonly_fields = ('page', 'location')
    form = SitemapNodeForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(
                PageSitemapNodeAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            title = obj.page.title_set.filter(
                    language=request.LANGUAGE_CODE).first()
            if title:
                form.base_fields['page_title'].initial = (
                        title.page_title)
                form.base_fields['meta_description'].initial = (
                        title.meta_description)
            form.base_fields['meta_keywords'].initial = obj.meta_keywords
        return form

    def save_model(self, request, obj, form, change):
        page_title = form.cleaned_data['page_title']
        meta_description = form.cleaned_data['meta_description']
        obj.meta_keywords = form.cleaned_data['meta_keywords']
        obj.page.title_set.filter(
                language=request.LANGUAGE_CODE).update(
                        meta_description=meta_description,
                        page_title=page_title)
        return super(PageSitemapNodeAdmin, self).save_model(
                request, obj, form, change)


class CategorySitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('category', 'include')
    fields = ('category', 'page_title', 'meta_description', 'meta_keywords',
              'changefreq', 'lastmod', 'location', 'priority', 'include')
    readonly_fields = ('category', 'location')
    form = SitemapNodeForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(CategorySitemapNodeAdmin, self).get_form(
                request, obj, **kwargs)
        if obj:
            form.base_fields['page_title'].initial = (
                    obj.category.page_title)
            form.base_fields['meta_description'].initial = (
                    obj.category.meta_description)
            form.base_fields['meta_keywords'].initial = (
                    obj.category.meta_keywords)
        return form

    def save_model(self, request, obj, form, change):
        super(CategorySitemapNodeAdmin, self).save_model(
                request, obj, form, change)
        obj.category.page_title = form.cleaned_data['page_title']
        obj.category.meta_description = form.cleaned_data['meta_description']
        obj.category.meta_keywords = form.cleaned_data['meta_keywords']
        obj.category.save()


class CustomSitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('location', 'include')
    fields = ('location', 'include')


admin.site.register(PageSitemapNode, PageSitemapNodeAdmin)
admin.site.register(CategorySitemapNode, CategorySitemapNodeAdmin)
admin.site.register(CustomSitemapNode, CustomSitemapNodeAdmin)
