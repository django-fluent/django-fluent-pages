"""
Admin screen for a region (``CmsRegion`` object).
"""
from django.contrib import admin
from ecms.models import CmsRegion


class CmsRegionInline(admin.TabularInline):
    model = CmsRegion
    extra = 1
    fieldsets = (
        (None, { 'fields': ('title', 'key', 'role'), }),
    )

class CmsLayoutAdmin(admin.ModelAdmin):
    # Config list page:
    list_display = ('title', 'key')
    fieldsets = (
        (None, { 'fields': ('title', 'key', 'template_path'), }),
    )
    inlines = [CmsRegionInline]
