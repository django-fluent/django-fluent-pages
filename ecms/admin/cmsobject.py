from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from mptt.admin import MPTTModelAdmin   # mptt 0.4
from ecms.models import CmsObject


class CmsObjectAdmin(MPTTModelAdmin):
    """
    Customisations for the admin interface.
    """

    # Config list page:
    list_display = ('slug', 'title', 'status', 'modification_date')
    #list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']

    # Config add/edit:
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ['parent']
    fieldsets = (
        (None, {
            'fields': ('title','status'),
        }),
        (_('SEO settings'), {
            'fields': ('slug', 'keywords', 'description'),
            #'classes': ('collapse',),
        }),
        (_('Publication settings'), {
            'fields': ('publication_date', 'expire_date', 'parent'),
            #'classes': ('collapse',),
        }),
    )
    radio_fields = {"status": admin.HORIZONTAL}


    def save_model(self, request, obj, form, change):
        """Automatically store the user in the author field."""
        if not change:
            obj.author = request.user
        obj.save()


    # ---- Custom actions ----

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=CmsObject.PUBLISHED)

        if rows_updated == 1:
            message = "1 page was marked as published."
        else:
            message = "%s pages were marked as published." % rows_updated
        self.message_user(request, message)


    make_published.short_description = _("Mark selected objects as published")
