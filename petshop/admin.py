from django.contrib.sites.admin import SiteAdmin, admin
from .models import SiteSettings


class SiteSettingsInline(admin.StackedInline):
    template = "admin/edit_inline/one_to_one.html"
    model = SiteSettings
    can_delete = False
    can_add = False


SiteAdmin.inlines = [SiteSettingsInline]
