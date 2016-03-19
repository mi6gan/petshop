from oscar.apps.payment.admin import *  # noqa

from .models import Provider, Source
from .providers import providers_pool


class ProviderAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'code')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            provider = providers_pool.get_by_code(obj.code)
            if provider and provider.admin_form_class:
                self.fields = (list(self.readonly_fields) + 
                        provider.admin_form_class.base_fields.keys())
                kwargs.update(form=provider.admin_form_class)
        return super(ProviderAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Provider, ProviderAdmin)
admin.site.unregister(Source)
admin.site.register(Source)
