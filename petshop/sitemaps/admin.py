from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import PageSitemapNode, CategorySitemapNode, CustomSitemapNode


class SitemapNodeForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)


class PageSitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('page', 'include')
    fields = ('page', 'changefreq', 'lastmod', 'location', 'priority', 'include')
    readonly_fields = ('page', 'location')
    form = SitemapNodeForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(
                PageSitemapNodeAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            title = obj.page.title_set.filter(
                    language=request.LANGUAGE_CODE).first()
            if title:
                form.base_fields['description'].initial = (
                        title.meta_description)
        return form

    def save_model(self, request, obj, form, change):
        description = form.cleaned_data['description']
        obj.page.title_set.filter(
                language=request.LANGUAGE_CODE).update(
                        meta_description=description)
        return super(PageSitemapNodeAdmin, self).save_model(
                request, obj, form, change)


class CategorySitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('category', 'include')
    fields = ('category', 'changefreq', 'lastmod', 'location', 'priority', 'include')
    readonly_fields = ('category', 'location')
    form = SitemapNodeForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(CategorySitemapNodeAdmin, self).get_form(
                request, obj, **kwargs)
        if obj:
            form.base_fields['description'].initial = (
                    obj.category.meta_description)
        return form

    def save_model(self, request, obj, form, change):
        super(CategorySitemapNodeAdmin, self).save_model(
                request, obj, form, change)
        obj.category.meta_description = form.cleaned_data['description']
        obj.category.save()


class CustomSitemapNodeAdmin(admin.ModelAdmin):
    list_display = ('location', 'include')
    fields = ('location', 'include')


admin.site.register(PageSitemapNode, PageSitemapNodeAdmin)
admin.site.register(CategorySitemapNode, CategorySitemapNodeAdmin)
admin.site.register(CustomSitemapNode, CustomSitemapNodeAdmin)
