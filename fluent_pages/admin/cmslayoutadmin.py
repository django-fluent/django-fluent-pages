"""
Admin screen for a layout (=template with metadata).
"""
from django.contrib import admin


class CmsLayoutAdmin(admin.ModelAdmin):
    # Config list page:
    list_display = ('title', 'key')
    fieldsets = (
        (None, { 'fields': ('title', 'key', 'template_path'), }),
    )
