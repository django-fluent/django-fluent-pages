"""
Admin screen for a layout (=template with metadata).
"""
from django.contrib import admin


class PageLayoutAdmin(admin.ModelAdmin):
    # Config list page:
    list_display = ('title', 'key')
    fieldsets = (
        (None, { 'fields': ('title', 'key', 'template_path'), }),
    )
    prepopulated_fields = {'key': ('title',)}
