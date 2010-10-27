from django.contrib import admin
from ecms.models import CmsSite, CmsObject, CmsPageItem
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin   # mptt 0.4


# -------- Custom screen definitions --------


class CmsObjectAdmin(MPTTModelAdmin):
    """
    Customisations for the admin interface.
    """

    # Config list page:
    list_display = ('slug', 'title', 'status', 'modification_date')
    list_filter = ('status', 'parent')
    search_fields = ('slug', 'title')
    actions = ['make_published']

    # Config add/edit:
    prepopulated_fields = { 'slug': ('title',), }
    raw_id_fields = ['parent']
    fieldsets = (
        (None, {
            'fields': ('title',),
        }),
        (_('Publication settings'), {
            'fields': ('status', 'publication_date', 'expire_date'),
            'classes': ('collapse',),
        }),
        (_('SEO settings'), {
            'fields': ('slug', 'keywords', 'description'),
            'classes': ('collapse',),
        })
    )
    radio_fields = {"status": admin.VERTICAL}

    
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


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(CmsSite)
admin.site.register(CmsPageItem)
admin.site.register(CmsObject, admin_class=CmsObjectAdmin)
