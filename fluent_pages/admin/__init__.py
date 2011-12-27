from django.contrib import admin
from fluent_pages.models import CmsSite, CmsObject, CmsLayout
from fluent_pages.admin.cmsobjectadmin import CmsObjectAdmin
from fluent_pages.admin.cmslayoutadmin import CmsLayoutAdmin

__all__ = ['CmsObjectAdmin', 'CmsLayoutAdmin']


# -------- Model registration --------

# Register the models with the admin site
admin.site.register(CmsSite)
admin.site.register(CmsObject, admin_class=CmsObjectAdmin)
admin.site.register(CmsLayout, admin_class=CmsLayoutAdmin)
